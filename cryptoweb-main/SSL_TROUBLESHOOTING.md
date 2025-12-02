# 🔧 SSL Connection Reset - TROUBLESHOOTING

## ⚠️ Issue: "Connection was reset" or "Can't reach this page"

Your server IS running correctly! The issue is browser security blocking the self-signed certificate.

---

## ✅ **SOLUTION 1: Use Chrome/Edge Special Flag** (RECOMMENDED)

### **Access via special Chrome URL:**

Instead of clicking "Advanced", type directly in address bar:

```
chrome://flags/#allow-insecure-localhost
```

**Then:**
1. Find "Allow invalid certificates for resources loaded from localhost"
2. Set to **"Enabled"**
3. Click **"Relaunch"**
4. Try https://localhost:5000 again
5. ✅ Should work without warnings!

---

## ✅ **SOLUTION 2: Try HTTP Instead** (EASIEST)

Since this is development, temporarily use HTTP:

### **Change SSL Setting:**

Open `app.py` and find line ~827:
```python
USE_SSL = True  # Change this to False
```

Change to:
```python
USE_SSL = False  # Temporarily disable SSL
```

**Then:**
1. Restart server (Ctrl+C, then run `python app.py`)
2. Use: **http://localhost:5000** (no 's')
3. ✅ Works immediately!

---

## ✅ **SOLUTION 3: Use Different Browser**

### **Try Firefox:**
Firefox often handles self-signed certificates better.

1. Open Firefox
2. Go to: https://localhost:5000
3. Click "Advanced"
4. Click "Accept the Risk and Continue"
5. ✅ Should work!

---

## ✅ **SOLUTION 4: Add Certificate Exception Manually**

### **In Chrome/Edge:**

1. Go to: `chrome://settings/security`
2. Click "Manage certificates"
3. Go to "Trusted Root Certification Authorities"
4. Import → Select `localhost.pem`
5. Restart browser
6. Try https://localhost:5000
7. ✅ Should work!

---

## ✅ **SOLUTION 5: Regenerate Certificate with SANs**

The certificate might need better configuration:

```powershell
cd C:\Users\USER\Downloads\cryptoweb-main\cryptoweb-main
.\venv\Scripts\Activate.ps1
python generate_ssl_cert.py
```

Say "y" to overwrite, then restart server.

---

## 🎯 **QUICK FIX (Recommended):**

**Just switch to HTTP for now:**

```powershell
# 1. Open app.py
# 2. Change line ~827: USE_SSL = False
# 3. Restart server
# 4. Use: http://localhost:5000
```

**This is FINE for development!** You still have:
- ✅ Kerberos authentication
- ✅ AES-256 encryption
- ✅ SHA-256 hashing
- ✅ All security features

The only difference is no TLS encryption in transit (which is okay on localhost).

---

## 📝 **Current Server Status:**

✅ Server IS running correctly
✅ Port 5000 IS listening
✅ Database IS connected
✅ No errors in the server

The issue is purely browser → SSL certificate validation.

---

## 🚀 **EASIEST SOLUTION:**

Use HTTP for development:

1. Edit `app.py` line 827: `USE_SSL = False`
2. Restart server
3. Access: **http://localhost:5000**
4. Everything works perfectly!

For production, you'd use a proper CA-signed certificate (Let's Encrypt, etc.)

---

**Choose the solution that works best for you!** 🎯

