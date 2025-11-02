# DealHound Usage Guide

## What DealHound Does

DealHound is a price tracking bot that automatically:
- Reads product URLs from a text file
- Opens each product page in a browser
- Extracts product name, price, and availability
- Saves data to CSV with timestamps
- Alerts you when prices drop below your threshold

## Input & Output

### Input Files

**products.txt** - List of product URLs (one per line):
```
https://www.amazon.com/dp/B08N5WRWNW
https://www.amazon.com/dp/B07H8QMZPV
```

**config.json** - Settings for threshold and email alerts

### Output

**results.csv** - All tracked data:
```csv
timestamp,product_name,price,availability,url
2024-01-15 14:30:45,Echo Dot (4th Gen),29.99,In Stock,https://...
```

**Console output** - Shows progress and alerts in real-time

## Quick Start

1. Add product URLs to `products.txt`
2. Set your price threshold in `config.json`
3. Run: `python dealhound.py`
4. Check `results.csv` for results

## How It Works

1. Reads URLs from `products.txt`
2. Opens Chrome browser automatically
3. For each product:
   - Navigates to the page
   - Extracts product name (tries multiple selectors)
   - Extracts price (handles various formats including decimals)
   - Checks availability status
   - Gets current timestamp
4. Saves everything to `results.csv`
5. Compares price to threshold - alerts if below
6. Moves to next product

## Adding More Products

**Option 1: Edit products.txt directly**
Just add one URL per line:
```
https://www.amazon.com/dp/NEW_PRODUCT_ID
```

**Option 2: Use terminal**
```bash
echo "https://www.amazon.com/dp/YOUR_PRODUCT_ID" >> products.txt
```

Then run:
```bash
python dealhound.py
```

## Common Commands

```bash
# Run normally
python dealhound.py

# Run without opening browser window
python dealhound.py --headless

# Use different product file
python dealhound.py --products my_products.txt

# View results
cat results.csv
```

## Tips

- Start with 1-2 products to test
- Make sure URLs are valid (test in browser first)
- Set a reasonable threshold in `config.json`
- Run regularly to track price changes over time

## Troubleshooting

**Problem: Element not found**
- Amazon may have changed their HTML
- Check the screenshot in `screenshots/` folder
- URL might be invalid

**Problem: Price shows as 0 or missing**
- Product might be out of stock
- Price selectors may need updating

**Problem: Browser doesn't open**
- Make sure Chrome is installed
- WebDriver Manager should auto-download driver

