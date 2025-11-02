# DealHound – Automated Price Tracker 🐾

A lightweight Python + Selenium project that monitors product prices and availability in real time.

Built to demonstrate real-world browser automation skills — from explicit waits and dynamic element handling to structured data collection.

Originally inspired by practical Selenium automation tutorials, DealHound shows how testing and data extraction can merge into clean, repeatable engineering practice.

## Overview

DealHound automatically checks product prices and availability from e-commerce websites (currently Amazon) and logs the data into a CSV file. It's designed as a portfolio project showcasing browser automation, robust error handling, and data collection patterns commonly used in QA automation and monitoring systems.

### What It Does

- Reads product URLs from a text file
- Opens each product page using Selenium WebDriver
- Extracts product name, current price, and availability status
- Saves results to `results.csv` with timestamps
- Sends email alerts when prices drop below a configured threshold
- Takes screenshots on errors for debugging
- Runs in headless mode for CI/server environments

### Why It Matters

This project demonstrates several key engineering practices:

- **Explicit Waits**: Uses `WebDriverWait` instead of `time.sleep()` for reliable element detection
- **Resilient Selectors**: Multiple fallback strategies for handling dynamic page layouts
- **Error Handling**: Graceful degradation when elements are missing or pages fail to load
- **Configuration Management**: JSON-based config with environment variable support
- **Structured Output**: CSV logging for easy data analysis and tracking over time

## Tech Stack

- **Python 3.11+**
- **Selenium 4.x** - Browser automation
- **WebDriver Manager** - Automatic ChromeDriver management
- **Pytest** - Unit testing framework
- **Pandas** - Optional data manipulation (included in dependencies)
- **python-dotenv** - Environment variable management

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- Google Chrome browser installed
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Subhadra-Mishra-iub/DealHound-PriceChecker.git
   cd DealHound-PriceChecker
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the project:**
   - Edit `config.json` to set your price threshold and preferences
   - Add product URLs to `products.txt` (one URL per line)
   - (Optional) Create a `.env` file for email credentials if using email alerts

### Environment Variables (Optional)

If you want to enable email alerts, create a `.env` file in the project root:

```env
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENT=recipient-email@gmail.com
```

**Note:** For Gmail, you'll need to use an [App Password](https://myaccount.google.com/apppasswords), not your regular account password.

## How It Works

### Step-by-Step Process

1. **Initialization:**
   - Loads configuration from `config.json`
   - Sets up Chrome WebDriver with WebDriver Manager (automatically downloads driver)
   - Creates `results.csv` with headers if it doesn't exist
   - Creates `screenshots/` directory for error captures

2. **Product Tracking:**
   - Reads URLs from `products.txt`
   - For each URL:
     - Opens the product page in Chrome
     - Waits for page elements using explicit waits (no hard-coded delays)
     - Extracts product name using multiple selector fallbacks
     - Extracts price with regex-based cleaning
     - Checks availability status
     - Appends data to `results.csv` with timestamp

3. **Alert Checking:**
   - Compares extracted price against threshold in `config.json`
   - Prints console alert if price is below threshold
   - Sends email alert if email alerts are enabled in config

4. **Error Handling:**
   - Takes screenshot if extraction fails
   - Logs errors without crashing
   - Continues processing remaining products

### Selector Strategy

DealHound uses a multi-selector approach to handle Amazon's dynamic page structure:

- **Product Name**: Tries `#productTitle`, `h1.a-size-large`, `#title span`, etc.
- **Price**: Attempts multiple selectors including `span.a-price-whole`, `#priceblock_ourprice`, etc.
- **Availability**: Checks `#availability span` and related elements

This approach prevents brittle automation that breaks when sites update their HTML.

## Usage

### Basic Usage

```bash
python dealhound.py
```

This will:
- Read URLs from `products.txt`
- Track all products and save results to `results.csv`
- Print results to console

### Headless Mode

Run without opening a browser window (useful for servers/CI):

```bash
python dealhound.py --headless
```

### Custom Configuration

```bash
python dealhound.py --products custom_products.txt --config custom_config.json
```

### Command-Line Options

```
--headless    Run browser in headless mode
--products    Path to products file (default: products.txt)
--config      Path to config file (default: config.json)
```

## Sample Output

### Console Output

```
Starting DealHound tracker for 3 product(s)...
------------------------------------------------------------

[1/3] Tracking: https://www.amazon.com/dp/B08N5WRWNW
  ✓ Product: Echo Dot (4th Gen) | Smart speaker with Alexa...
  ✓ Price: $29.99
  ✓ Availability: In Stock

[2/3] Tracking: https://www.amazon.com/dp/B07H8QMZPV
  ✓ Product: Fire TV Stick 4K streaming device...
  ✓ Price: $39.99
  ✓ Availability: In Stock

[3/3] Tracking: https://www.amazon.com/dp/B08C1W5N87
  ✓ Product: Ring Video Doorbell – 1080p HD video...
  ✓ Price: $99.99
  ✓ Availability: In Stock

------------------------------------------------------------
Tracking complete! Results saved to results.csv
```

### CSV Output (`results.csv`)

```csv
timestamp,product_name,price,availability,url
2024-01-15 10:30:45,Echo Dot (4th Gen),29.99,In Stock,https://www.amazon.com/dp/B08N5WRWNW
2024-01-15 10:31:12,Fire TV Stick 4K,39.99,In Stock,https://www.amazon.com/dp/B07H8QMZPV
2024-01-15 10:31:38,Ring Video Doorbell,99.99,In Stock,https://www.amazon.com/dp/B08C1W5N87
```

## Testing

Run the test suite:

```bash
pytest tests/test_dealhound.py -v
```

The tests cover:
- Configuration loading
- CSV file initialization and writing
- Price threshold checking
- Data validation
- Mocked extraction logic

## Configuration Reference

### `config.json`

```json
{
  "price_threshold": 50.0,
  "email_alerts": {
    "enabled": false,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "",
    "recipient_email": ""
  },
  "screenshot_on_error": true,
  "implicit_wait_timeout": 10,
  "explicit_wait_timeout": 20
}
```

- **price_threshold**: Trigger alert if price drops below this value
- **email_alerts.enabled**: Enable/disable email notifications
- **screenshot_on_error**: Take screenshot when extraction fails
- **implicit_wait_timeout**: Default wait time for element presence
- **explicit_wait_timeout**: Maximum wait time for specific elements

## Project Structure

```
dealhound/
├── dealhound.py           # Main script
├── config.json            # Configuration file
├── products.txt           # Product URLs (one per line)
├── results.csv            # Generated results file
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .gitignore            # Git ignore rules
├── screenshots/           # Error screenshots (created automatically)
└── tests/
    └── test_dealhound.py  # Test suite
```

## Future Enhancements

Potential improvements for the project:

- **Multi-site Support**: Add scrapers for eBay, Best Buy, Target, etc.
- **Scheduling**: Run automatically at intervals using `cron` or `schedule` library
- **Price History**: Track price changes over time and generate charts
- **Database Storage**: Replace CSV with SQLite or PostgreSQL for better querying
- **Web Dashboard**: Build a Flask/FastAPI dashboard to visualize price trends
- **API Integration**: Connect to price tracking APIs for more reliable data
- **Notification Channels**: Add Slack, Discord, or SMS alerts
- **Product Comparison**: Compare prices across multiple retailers

## Ethical Use Disclaimer

**Important:** This project is designed for educational and personal use only.

- Automation should respect website terms of service
- Use reasonable delays between requests to avoid overloading servers
- Consider using official APIs when available
- This tool is not intended for commercial scraping or resale purposes
- Always check a website's `robots.txt` and terms of service before automating

The author and contributors are not responsible for misuse of this software.

## Challenges Faced

Building this project came with several interesting challenges:

**Dynamic Page Structure**: Amazon frequently changes their HTML structure, which broke my initial selectors. I solved this by implementing a multi-selector fallback strategy - if one selector fails, it tries the next one. This made the scraper much more resilient.

**Price Format Variations**: Prices come in different formats - sometimes with decimals ($23.97), sometimes without ($23), and Amazon sometimes splits them into separate HTML elements (whole dollars and cents). I had to write regex patterns and handle multiple CSS selectors to catch all cases.

**Timing Issues**: Initially used `time.sleep()` which was unreliable - sometimes pages loaded faster, sometimes slower. Switching to `WebDriverWait` with explicit conditions solved this and made the code faster and more reliable.

**Decimal Precision**: Early versions lost decimal precision when saving to CSV (showing 23.0 instead of 23.97). Fixed by explicitly formatting prices to 2 decimal places when writing to CSV.

**Email Configuration**: Getting Gmail SMTP to work required using App Passwords instead of regular passwords, and handling missing credentials gracefully without crashing the entire program.

These challenges taught me a lot about robust web scraping - always have fallbacks, handle edge cases, and never assume data will be in the format you expect.

## License

This project is provided as-is for educational purposes. Feel free to use and modify it for learning and personal projects.

## Contributing

Contributions, issues, and feature requests are welcome! This is a learning project, so feel free to experiment and share improvements.

---

**Built with** ❤️ **using Python and Selenium**

For questions or feedback, please open an issue on GitHub.
