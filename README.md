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

When you run DealHound, you'll see real-time progress for each product:

```
Starting DealHound tracker for 2 product(s)...
------------------------------------------------------------

[1/2] Tracking: https://www.amazon.com/.../dp/B01DHKOS3O...
  ✓ Product: Multivitamin for Women – Methylated Womens Multivitamins...
  ✓ Price: $23.97
  ✓ Availability: In Stock

🚨 ALERT: Multivitamin for Women... is below threshold!
   Current Price: $23.97
   Threshold: $25.00

[2/2] Tracking: https://www.amazon.com/.../dp/B0DV67FJYB...
  ✓ Product: Forever 21 Womens Hooded Zip-up Sweater
  ✓ Price: $11.44
  ✓ Availability: In Stock

🚨 ALERT: Forever 21 Womens Hooded Zip-up Sweater is below threshold!
   Current Price: $11.44
   Threshold: $25.00

------------------------------------------------------------
Tracking complete! Results saved to results.csv
```

The console shows immediate feedback - you know right away if prices are below your threshold!

### CSV Output (`results.csv`)

The `results.csv` file tracks all price checks with timestamps, allowing you to see price history over time. Each run appends new data, building a price tracking database.

**Example from actual tracking data:**
```csv
timestamp,product_name,price,availability,url
2025-11-02 18:48:35,Multivitamin for Women...,23.97,In Stock,https://www.amazon.com/...
2025-11-02 18:49:28,Forever 21 Womens Hooded Zip-up Sweater,11.44,In Stock,https://www.amazon.com/...
```

**Key Features:**
- **Timestamp**: Records exactly when each price check occurred
- **Price**: Preserved with full decimal precision (23.97, not 23.0)
- **Availability**: Tracks stock status (In Stock/Out of Stock)
- **URL**: Links back to the original product page

This CSV format makes it easy to:
- Track price changes over time
- Import into Excel/Google Sheets for analysis
- Create price history charts
- Identify best times to buy

## Working Example

The repository includes a `results.csv` file with real tracking data from actual Amazon products:

- **Multivitamin for Women**: Tracked at $23.97 on Nov 2, 2025
- **Forever 21 Sweater**: Tracked at $11.44 on Nov 2, 2025

This demonstrates the system working with:
- ✅ Full decimal precision (23.97 preserved correctly)
- ✅ Timestamps for price history tracking
- ✅ Product name extraction from Amazon pages
- ✅ Availability status detection

You can open `results.csv` in Excel or Google Sheets to see the tracked data and analyze price patterns over time.

## Testing

Run the test suite to verify everything works:

```bash
pytest tests/test_dealhound.py -v
```

The tests cover:
- Configuration loading
- CSV file initialization and writing
- Price threshold checking
- Data validation
- Mocked extraction logic

All tests should pass, confirming the core functionality works correctly.

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
DealHound-PriceChecker/
├── dealhound.py           # Main automation script
├── config.json            # Settings (threshold, email alerts)
├── products.txt           # Product URLs to track (one per line)
├── results.csv            # Price tracking data (appended on each run)
├── requirements.txt       # Python dependencies
├── LICENSE                # MIT License
├── README.md              # This file
├── .gitignore            # Git ignore rules
├── env.example           # Email configuration template
├── screenshots/           # Error screenshots (auto-created)
├── tests/
│   ├── __init__.py
│   └── test_dealhound.py  # Unit tests
└── docs/
    ├── USAGE_GUIDE.md     # How to use DealHound
    ├── EMAIL_SETUP.md     # Email alert configuration
    └── TESTING_GUIDE.md   # Testing instructions
```

**Key Files:**
- `dealhound.py`: Core automation logic with Selenium
- `results.csv`: Contains actual tracking data with timestamps (see repo for sample data)
- `config.json`: Customize price thresholds and email settings
- `products.txt`: Simple text file - just add URLs one per line

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

You are free to:
- Use the code for personal or commercial projects
- Modify and adapt it to your needs
- Distribute and share it

The MIT License is one of the most permissive open-source licenses, allowing maximum freedom while providing minimal restrictions.

## Contributing

Contributions, issues, and feature requests are welcome! This is a learning project, so feel free to experiment and share improvements.

---

## About the Data

The `results.csv` file included in this repository contains real tracking data from live Amazon products. This serves as proof that the system works correctly:

- Prices are extracted with full decimal precision
- Timestamps are accurate and sequential
- Product names are correctly captured
- Availability status is properly detected

Each time you run DealHound, new rows are appended to `results.csv`, building a price history database that you can analyze in Excel, Python (pandas), or any data analysis tool.

---

**Built with** ❤️ **using Python and Selenium**

For questions or feedback, please open an issue on GitHub.
