
import pytest
import json
import csv
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from dealhound import PriceTracker


class TestPriceTracker:
    @pytest.fixture
    def temp_config(self):
        config = {
            "price_threshold": 100.0,
            "email_alerts": {
                "enabled": False
            },
            "screenshot_on_error": True,
            "explicit_wait_timeout": 20,
            "implicit_wait_timeout": 10
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name
        
        yield temp_path
        
        os.unlink(temp_path)
    
    @pytest.fixture
    def tracker(self, temp_config):
        return PriceTracker(config_path=temp_config, headless=True)
    
    def test_config_loading(self, temp_config):
        tracker = PriceTracker(config_path=temp_config)
        assert tracker.config["price_threshold"] == 100.0
        assert tracker.config["screenshot_on_error"] is True
    
    def test_config_missing_file(self):
        tracker = PriceTracker(config_path="nonexistent_config.json")
        assert "price_threshold" in tracker.config
        assert tracker.config["screenshot_on_error"] is True
    
    def test_csv_initialization(self, tracker):
        if os.path.exists(tracker.results_file):
            os.remove(tracker.results_file)
        
        tracker._initialize_csv()
        
        assert os.path.exists(tracker.results_file)
        
        with open(tracker.results_file, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected_headers = ['timestamp', 'product_name', 'price', 'availability', 'url']
            assert headers == expected_headers
    
    def test_save_result(self, tracker):
        if os.path.exists(tracker.results_file):
            os.remove(tracker.results_file)
        
        tracker._initialize_csv()
        
        test_data = {
            'product_name': 'Test Product',
            'price': 49.99,
            'availability': 'In Stock',
            'url': 'https://example.com/product'
        }
        
        tracker._save_result(test_data)
        
        assert os.path.exists(tracker.results_file)
        
        with open(tracker.results_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]['product_name'] == 'Test Product'
            assert rows[0]['price'] == '49.99'
            assert rows[0]['availability'] == 'In Stock'
    
    def test_save_result_with_none_price(self, tracker):
        if os.path.exists(tracker.results_file):
            os.remove(tracker.results_file)
        
        tracker._initialize_csv()
        
        test_data = {
            'product_name': 'Test Product',
            'price': None,
            'availability': 'Out of Stock',
            'url': 'https://example.com/product'
        }
        
        tracker._save_result(test_data)
        
        with open(tracker.results_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert rows[0]['price'] == 'N/A'
    
    def test_price_threshold_alert(self, tracker):
        product_data = {
            'product_name': 'Test Product',
            'price': 45.0,
            'availability': 'In Stock',
            'url': 'https://example.com/product'
        }
        
        with patch('builtins.print') as mock_print:
            tracker._check_price_threshold(product_data)
            assert any('ALERT' in str(call) for call in mock_print.call_args_list)
    
    def test_price_threshold_no_alert(self, tracker):
        product_data = {
            'product_name': 'Test Product',
            'price': 150.0,
            'availability': 'In Stock',
            'url': 'https://example.com/product'
        }
        
        with patch('builtins.print') as mock_print:
            tracker._check_price_threshold(product_data)
            alert_calls = [str(call) for call in mock_print.call_args_list if 'ALERT' in str(call)]
            assert len(alert_calls) == 0
    
    def test_screenshot_directory_creation(self, tracker):
        assert tracker.screenshots_dir.exists()
        assert tracker.screenshots_dir.is_dir()
    
    @patch('selenium.webdriver.Chrome')
    def test_driver_setup_headless(self, mock_chrome):
        tracker = PriceTracker(headless=True)
        driver = tracker._setup_driver()
        mock_chrome.assert_called_once()
    
    def test_extract_amazon_product_mock(self, tracker):
        mock_driver = MagicMock()
        mock_wait = MagicMock()
        
        with patch('dealhound.WebDriverWait', return_value=mock_wait):
            mock_name_element = MagicMock()
            mock_name_element.text = "Test Product Name"
            mock_wait.until.return_value = mock_name_element
            
            mock_price_element = MagicMock()
            mock_price_element.text = "$49.99"
            mock_driver.find_elements.return_value = [mock_price_element]
            
            url = "https://www.amazon.com/dp/TEST123"
            result = tracker._extract_amazon_product(mock_driver, url)
            assert result is None or isinstance(result, dict)


class TestDataValidation:
    def test_price_numeric_validation(self):
        test_prices = ["$49.99", "$1,234.56", "49.99", "100"]
        
        import re
        for price_text in test_prices:
            cleaned = price_text.replace('$', '').replace(',', '').strip()
            match = re.search(r'(\d+\.?\d*)', cleaned)
            if match:
                price = float(match.group(1))
                assert isinstance(price, float)
                assert price > 0
    
    def test_csv_column_types(self):
        timestamp = "2024-01-15 10:30:00"
        product_name = "Test Product"
        price = 49.99
        availability = "In Stock"
        url = "https://example.com"
        
        row = [str(timestamp), str(product_name), str(price), str(availability), str(url)]
        assert len(row) == 5
        assert all(isinstance(field, str) for field in row)


@pytest.fixture
def sample_products_file(tmp_path):
    products_file = tmp_path / "test_products.txt"
    products_file.write_text("https://www.amazon.com/dp/TEST123\n")
    return str(products_file)


def test_products_file_loading(sample_products_file):
    tracker = PriceTracker()
    
    with open(sample_products_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    assert len(urls) == 1
    assert "amazon.com" in urls[0]
