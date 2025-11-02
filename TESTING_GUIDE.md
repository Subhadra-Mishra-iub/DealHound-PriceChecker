# DealHound Testing Guide

## 📖 How DealHound Works

### Step-by-Step Process

1. **Initialization Phase:**
   ```
   ┌─────────────────────────────────────┐
   │ Load config.json                   │
   │ → Set price threshold              │
   │ → Configure email settings         │
   └─────────────────────────────────────┘
           ↓
   ┌─────────────────────────────────────┐
   │ Read products.txt                   │
   │ → Parse URLs (one per line)         │
   └─────────────────────────────────────┘
           ↓
   ┌─────────────────────────────────────┐
   │ Setup Chrome WebDriver              │
   │ → WebDriver Manager auto-downloads │
   │ → Configure browser options        │
   └─────────────────────────────────────┘
   ```

2. **Product Tracking Phase (for each URL):**
   ```
   ┌─────────────────────────────────────┐
   │ Navigate to product page            │
   │ → driver.get(url)                  │
   └─────────────────────────────────────┘
           ↓
   ┌─────────────────────────────────────┐
   │ Extract Product Name                │
   │ → Try multiple CSS selectors        │
   │ → #productTitle, h1.a-size-large    │
   │ → Wait with WebDriverWait           │
   └─────────────────────────────────────┘
           ↓
   ┌─────────────────────────────────────┐
   │ Extract Price                       │
   │ → Try price selectors               │
   │ → Clean with regex ($, commas)      │
   │ → Convert to float                  │
   └─────────────────────────────────────┘
           ↓
   ┌─────────────────────────────────────┐
   │ Check Availability                  │
   │ → Find availability element         │
   │ → Parse "In Stock" / "Out of Stock" │
   └─────────────────────────────────────┘
           ↓
   ┌─────────────────────────────────────┐
   │ Save to CSV                         │
   │ → Append row with timestamp         │
   │ → results.csv                       │
   └─────────────────────────────────────┘
           ↓
   ┌─────────────────────────────────────┐
   │ Check Price Threshold               │
   │ → Compare price vs threshold        │
   │ → Alert if below threshold          │
   └─────────────────────────────────────┘
   ```

3. **Error Handling:**
   - If element not found → Try next selector
   - If all selectors fail → Take screenshot, log error, continue
   - If page fails to load → Screenshot saved, skip to next URL

---

## 🧪 Testing Methods

### Method 1: Unit Tests (Recommended First)

Run the test suite to verify all core functionality:

```bash
# Run all tests
pytest tests/test_dealhound.py -v

# Run specific test
pytest tests/test_dealhound.py::TestPriceTracker::test_price_threshold_alert -v

# Run with output
pytest tests/test_dealhound.py -v -s
```

**What the tests verify:**
- ✅ Configuration loading
- ✅ CSV file creation and writing
- ✅ Price threshold logic
- ✅ Data validation
- ✅ Error handling for None values

### Method 2: Dry Run Test (Check Configuration)

Test that everything is configured correctly without running browser:

```bash
# Check if files exist
ls -la products.txt config.json

# Verify Python can import the module
python3 -c "from dealhound import PriceTracker; print('Import successful!')"

# Check if dependencies are installed
pip list | grep -E "(selenium|webdriver|pytest)"
```

### Method 3: Single Product Test

Test with just one product URL first:

**Step 1:** Create a test products file:
```bash
echo "https://www.amazon.com/dp/B08N5WRWNW" > test_product.txt
```

**Step 2:** Run with the test file:
```bash
python dealhound.py --products test_product.txt
```

**Expected Output:**
```
Starting DealHound tracker for 1 product(s)...
------------------------------------------------------------

[1/1] Tracking: https://www.amazon.com/dp/B08N5WRWNW
  ✓ Product: Echo Dot (4th Gen) | Smart speaker with Alexa...
  ✓ Price: $29.99
  ✓ Availability: In Stock

------------------------------------------------------------
Tracking complete! Results saved to results.csv
```

**Step 3:** Verify results.csv was created:
```bash
cat results.csv
```

### Method 4: Full Test Run

Test with all products in `products.txt`:

```bash
# Normal mode (browser visible)
python dealhound.py

# Headless mode (no browser window)
python dealhound.py --headless
```

**Watch for:**
- Browser opens and navigates to each URL
- Product information appears in console
- `results.csv` file is created/updated
- Screenshots saved if errors occur

### Method 5: Test Price Alert

Test the price alert functionality:

**Step 1:** Edit `config.json`:
```json
{
  "price_threshold": 1000.0  // Set high to trigger alert
}
```

**Step 2:** Run with a product that costs less than threshold:
```bash
python dealhound.py
```

**Expected:** You should see:
```
🚨 ALERT: [Product Name] is below threshold!
   Current Price: $29.99
   Threshold: $1000.00
```

---

## 🔍 Verification Checklist

After running tests, verify:

- [ ] `results.csv` exists and has headers
- [ ] CSV contains rows with product data
- [ ] Screenshots directory exists (created automatically)
- [ ] Console shows product names, prices, availability
- [ ] No Python errors or tracebacks
- [ ] Browser closes after completion (or stays open in debug mode)

---

## 🐛 Troubleshooting

### Issue: "ChromeDriver not found"
**Solution:** WebDriver Manager should auto-download it. If not:
```bash
pip install --upgrade webdriver-manager
```

### Issue: "No such file: products.txt"
**Solution:** Make sure you're in the project directory:
```bash
pwd  # Should show: .../DealHound-PriceChecker
ls products.txt  # Should exist
```

### Issue: "Element not found" errors
**Solution:** Amazon's HTML may have changed. Check:
- Internet connection is working
- URL is valid (open it manually in browser)
- Selectors may need updating (see code comments)

### Issue: Tests fail
**Solution:** Make sure you're using Python 3.11+:
```bash
python3 --version
pip install -r requirements.txt
```

### Issue: Browser opens but nothing happens
**Solution:** Check for console errors. Try headless mode:
```bash
python dealhound.py --headless
```

---

## 📊 Testing Different Scenarios

### Test 1: Normal Operation
```bash
python dealhound.py
```
✅ Should extract all products successfully

### Test 2: Empty Products File
```bash
echo "" > empty.txt
python dealhound.py --products empty.txt
```
✅ Should print "No valid URLs found"

### Test 3: Invalid URL
```bash
echo "https://invalid-url-test.com" > invalid.txt
python dealhound.py --products invalid.txt
```
✅ Should handle gracefully with error message

### Test 4: Missing Config
```bash
mv config.json config.json.bak
python dealhound.py
mv config.json.bak config.json
```
✅ Should use default configuration

### Test 5: Headless Mode
```bash
python dealhound.py --headless
```
✅ Should run without opening browser window

---

## 🎯 Expected Test Results

### Unit Tests
```
13 passed in 0.62s
```

### Manual Run
```
Starting DealHound tracker for 3 product(s)...
------------------------------------------------------------
[1/3] Tracking: [URL]
  ✓ Product: [Name]
  ✓ Price: $[Amount]
  ✓ Availability: [Status]
...
------------------------------------------------------------
Tracking complete! Results saved to results.csv
```

### CSV Output
```csv
timestamp,product_name,price,availability,url
2024-01-15 10:30:45,Product Name,29.99,In Stock,https://...
```

---

## 🚀 Quick Start Testing

**Fastest way to verify everything works:**

```bash
# 1. Install dependencies (if not done)
pip install -r requirements.txt

# 2. Run unit tests
pytest tests/test_dealhound.py -v

# 3. Run with one product
echo "https://www.amazon.com/dp/B08N5WRWNW" > test.txt
python dealhound.py --products test.txt

# 4. Check results
cat results.csv
```

---

## 📝 Testing Notes

- **First run may be slower** - WebDriver Manager downloads ChromeDriver
- **Amazon may rate-limit** - If you run too many times quickly
- **Selectors may need updates** - Amazon changes HTML frequently
- **Screenshots help debug** - Check `screenshots/` folder if errors occur

---

## ✅ Success Criteria

You know DealHound is working correctly when:

1. ✅ All 13 unit tests pass
2. ✅ `results.csv` is created with proper headers
3. ✅ Product data is extracted and displayed in console
4. ✅ CSV contains timestamp, name, price, availability, URL
5. ✅ No Python errors or crashes
6. ✅ Browser automation runs smoothly

---

Happy Testing! 🎉
