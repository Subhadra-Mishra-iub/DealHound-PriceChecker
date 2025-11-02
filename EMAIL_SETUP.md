# 📧 Email Alert Setup Guide

## Quick Answer to Your Questions:

**1. Which file has the threshold?** 
- ✅ `config.json` - The `price_threshold` is set to **$25.00**

**2. Will you get email notifications?**
- ✅ Yes! Email alerts are now **enabled** in `config.json`
- ✅ Your email is configured in `config.json`

**3. How will you know?**
- You'll get an **email notification** when price drops below threshold
- You'll also see a **console alert** message when running

---

## ⚠️ Important: Gmail App Password Required

To send emails from DealHound, you need to set up a **Gmail App Password** (not your regular password).

### Step-by-Step Setup:

1. **Go to Google Account Settings:**
   - Visit: https://myaccount.google.com/apppasswords
   - Or: Google Account → Security → 2-Step Verification → App Passwords

2. **Create App Password:**
   - Select app: "Mail"
   - Select device: "Other (Custom name)" → Enter "DealHound"
   - Click "Generate"
   - **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)

3. **Create .env file:**
   ```bash
   cp env.example .env
   ```

4. **Edit .env file:**
   ```bash
   nano .env
   # or
   code .env
   ```

5. **Add your email and app password:**
   ```env
   EMAIL_SENDER=your-email@gmail.com
   EMAIL_PASSWORD=your-16-character-app-password-here
   EMAIL_RECIPIENT=your-email@gmail.com
   ```
   
   **Important:** 
   - Use the **16-character app password** (remove spaces: `abcdefghijklmnop`)
   - Do NOT use your regular Gmail password
   - The `.env` file is already in `.gitignore` so it won't be committed

6. **Save the file**

7. **Test it:**
   ```bash
   python dealhound.py
   ```

---

## 📊 Current Configuration:

**config.json:**
```json
{
  "price_threshold": 25.0,
  "email_alerts": {
    "enabled": true,
    "recipient_email": "your-email@gmail.com"
  }
}
```

**What this means:**
- Products below your threshold will trigger alerts
- You'll get an email notification to the configured address

---

## 🧪 Testing Email Alerts:

After setting up the `.env` file:

```bash
# Run DealHound
python dealhound.py --headless

# Check your email inbox
# You should receive emails for products below $25
```

---

## 📧 Email Alert Example:

**Subject:** DealHound Alert: Multivitamin for Women Price Drop!

**Body:**
```
DealHound Price Alert!

Product: Multivitamin for Women – Methylated Womens Multivitamins...
Current Price: $23.00
Threshold: $25.00
Availability: In Stock
URL: https://www.amazon.com/...
```

---

## ✅ Checklist:

- [x] Threshold configured in config.json
- [x] Email alerts enabled in config.json
- [ ] Your email configured in config.json and .env file
- [ ] Create `.env` file with Gmail App Password (you need to do this)
- [ ] Test by running `python dealhound.py`

---

## 🔒 Security Note:

- The `.env` file is in `.gitignore` - it will NOT be committed to GitHub
- Your password stays local and secure
- Use App Password (not your regular Gmail password)

---

**Once you set up the `.env` file, DealHound will send you email alerts automatically!** 🎉
