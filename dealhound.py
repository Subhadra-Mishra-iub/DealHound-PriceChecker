#!/usr/bin/env python3

import json
import csv
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()


class PriceTracker:
    def __init__(self, config_path: str = "config.json", headless: bool = False):
        self.config = self._load_config(config_path)
        self.headless = headless
        self.results_file = "results.csv"
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self._initialize_csv()
    
    def _load_config(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_path} not found. Using defaults.")
            return {
                "price_threshold": 50.0,
                "email_alerts": {"enabled": False},
                "screenshot_on_error": True,
                "explicit_wait_timeout": 20
            }
    
    def _initialize_csv(self):
        if not os.path.exists(self.results_file):
            with open(self.results_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'product_name', 'price', 'availability', 'url'])
    
    def _setup_driver(self) -> webdriver.Chrome:
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(self.config.get("implicit_wait_timeout", 10))
        
        return driver
    
    def _extract_amazon_product(self, driver: webdriver.Chrome, url: str) -> Optional[Dict]:
        wait_timeout = self.config.get("explicit_wait_timeout", 20)
        wait = WebDriverWait(driver, wait_timeout)
        
        try:
            product_name = None
            price = None
            availability = "Unknown"
            
            name_selectors = [
                "span#productTitle",
                "h1.a-size-large",
                "#title span",
                "h1 span"
            ]
            
            for selector in name_selectors:
                try:
                    name_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    product_name = name_element.text.strip()
                    break
                except TimeoutException:
                    continue
            
            if not product_name:
                print(f"Warning: Could not extract product name from {url}")
                return None
            
            price_selectors = [
                "span.a-price-whole",
                "span.a-offscreen",
                "#priceblock_ourprice",
                "#priceblock_dealprice",
                ".a-price .a-offscreen",
                "span[data-a-color='price'] span.a-offscreen",
                ".a-price span"
            ]
            
            for selector in price_selectors:
                try:
                    price_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if price_elements:
                        price_text = price_elements[0].text.strip()
                        
                        try:
                            price_fraction = driver.find_element(By.CSS_SELECTOR, "span.a-price-fraction")
                            if price_fraction:
                                fraction_text = price_fraction.text.strip()
                                price_text = f"{price_text}.{fraction_text}"
                        except NoSuchElementException:
                            pass
                        
                        price_text = price_text.replace('$', '').replace(',', '').strip()
                        if price_text:
                            try:
                                import re
                                price_match = re.search(r'(\d+\.?\d*)', price_text)
                                if price_match:
                                    price_value = float(price_match.group(1))
                                    if price_value > 0 and price_value < 1000000:
                                        price = price_value
                                        break
                            except (ValueError, AttributeError):
                                continue
                except (NoSuchElementException, IndexError):
                    continue
            
            availability_selectors = [
                "#availability span",
                "#availability",
                "#stockAvailability",
                "div#availability"
            ]
            
            for selector in availability_selectors:
                try:
                    avail_element = driver.find_element(By.CSS_SELECTOR, selector)
                    availability_text = avail_element.text.strip().lower()
                    
                    if 'in stock' in availability_text or 'available' in availability_text:
                        availability = "In Stock"
                        break
                    elif 'out of stock' in availability_text or 'unavailable' in availability_text:
                        availability = "Out of Stock"
                        break
                except NoSuchElementException:
                    continue
            
            if availability == "Unknown" and price:
                availability = "In Stock"
            
            return {
                'product_name': product_name,
                'price': price,
                'availability': availability,
                'url': url
            }
            
        except Exception as e:
            print(f"Error extracting data from {url}: {str(e)}")
            if self.config.get("screenshot_on_error", True):
                self._take_screenshot(driver, url)
            return None
    
    def _take_screenshot(self, driver: webdriver.Chrome, url: str):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_url = url.replace("https://", "").replace("http://", "").replace("/", "_")[:50]
            filename = f"{timestamp}_{safe_url}.png"
            screenshot_path = self.screenshots_dir / filename
            driver.save_screenshot(str(screenshot_path))
            print(f"Screenshot saved to {screenshot_path}")
        except Exception as e:
            print(f"Failed to take screenshot: {str(e)}")
    
    def _save_result(self, product_data: Dict):
        if not product_data:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        price_value = product_data.get('price')
        if price_value is None:
            price_str = 'N/A'
        else:
            price_str = f"{float(price_value):.2f}"
        
        with open(self.results_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                product_data.get('product_name', 'N/A'),
                price_str,
                product_data.get('availability', 'N/A'),
                product_data.get('url', 'N/A')
            ])
    
    def _check_price_threshold(self, product_data: Dict):
        price = product_data.get('price')
        if price is None:
            return
        
        threshold = self.config.get("price_threshold", float('inf'))
        
        if price < threshold:
            product_name = product_data.get('product_name', 'Product')
            print(f"\n🚨 ALERT: {product_name} is below threshold!")
            print(f"   Current Price: ${price:.2f}")
            print(f"   Threshold: ${threshold:.2f}")
            
            if self.config.get("email_alerts", {}).get("enabled", False):
                self._send_email_alert(product_data, price, threshold)
    
    def _send_email_alert(self, product_data: Dict, price: float, threshold: float):
        email_config = self.config.get("email_alerts", {})
        
        sender_email = os.getenv("EMAIL_SENDER") or email_config.get("sender_email", "")
        password = os.getenv("EMAIL_PASSWORD", "")
        recipient_email = os.getenv("EMAIL_RECIPIENT") or email_config.get("recipient_email", "")
        
        if not all([sender_email, password, recipient_email]):
            print("Email alert enabled but credentials missing. Check .env file or config.json")
            return
        
        try:
            smtp_server = email_config.get("smtp_server", "smtp.gmail.com")
            smtp_port = email_config.get("smtp_port", 587)
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"DealHound Alert: {product_data.get('product_name', 'Product')} Price Drop!"
            
            body = f"""
            DealHound Price Alert!
            
            Product: {product_data.get('product_name', 'N/A')}
            Current Price: ${price:.2f}
            Threshold: ${threshold:.2f}
            Availability: {product_data.get('availability', 'N/A')}
            URL: {product_data.get('url', 'N/A')}
            
            The price has dropped below your threshold!
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
            server.quit()
            
            print("   ✓ Email alert sent successfully!")
            
        except Exception as e:
            print(f"   ✗ Failed to send email alert: {str(e)}")
    
    def track_products(self, products_file: str = "products.txt"):
        if not os.path.exists(products_file):
            print(f"Error: Products file '{products_file}' not found.")
            return
        
        with open(products_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not urls:
            print("No valid URLs found in products file.")
            return
        
        print(f"Starting DealHound tracker for {len(urls)} product(s)...")
        print("-" * 60)
        
        driver = None
        try:
            driver = self._setup_driver()
            
            for idx, url in enumerate(urls, 1):
                print(f"\n[{idx}/{len(urls)}] Tracking: {url}")
                
                try:
                    driver.get(url)
                    
                    import time
                    time.sleep(2)
                    
                    if "amazon" in url.lower():
                        product_data = self._extract_amazon_product(driver, url)
                    else:
                        print(f"Unsupported domain for URL: {url}")
                        print("Currently only Amazon URLs are supported.")
                        continue
                    
                    if product_data:
                        print(f"  ✓ Product: {product_data['product_name'][:60]}...")
                        print(f"  ✓ Price: ${product_data['price']:.2f}" if product_data.get('price') else "  ✓ Price: N/A")
                        print(f"  ✓ Availability: {product_data['availability']}")
                        
                        self._save_result(product_data)
                        self._check_price_threshold(product_data)
                    else:
                        print("  ✗ Failed to extract product data")
                
                except Exception as e:
                    print(f"  ✗ Error processing {url}: {str(e)}")
                    if self.config.get("screenshot_on_error", True) and driver:
                        self._take_screenshot(driver, url)
            
            print("\n" + "-" * 60)
            print(f"Tracking complete! Results saved to {self.results_file}")
            
        except Exception as e:
            print(f"Fatal error: {str(e)}")
            sys.exit(1)
        finally:
            if driver:
                driver.quit()


def main():
    parser = argparse.ArgumentParser(
        description="DealHound - Automated Price Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (for CI/server environments)'
    )
    parser.add_argument(
        '--products',
        type=str,
        default='products.txt',
        help='Path to products file (default: products.txt)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to config file (default: config.json)'
    )
    
    args = parser.parse_args()
    
    tracker = PriceTracker(config_path=args.config, headless=args.headless)
    tracker.track_products(products_file=args.products)


if __name__ == "__main__":
    main()
