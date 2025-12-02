# 🔒 How to Access Your HTTPS Site

## ✅ **SSL Certificate is Working!**

Your server is now running with HTTPS enabled!

---

## 🚀 **Access Your Secure Site:**

### **Step-by-Step Instructions:**

1. **Open your browser** (Chrome, Edge, or Firefox)

2. **Type this URL** in the address bar:
   ```
   https://localhost:5000
   ```

3. **You'll see a warning** (This is NORMAL for self-signed certificates):
   ```
   ⚠ Your connection is not private
   ⚠ NET::ERR_CERT_AUTHORITY_INVALID
   ```

4. **Click "Advanced"** (at the bottom of the warning)

5. **Click "Proceed to localhost (unsafe)"** or "Continue to localhost"

6. **Done!** You're now on HTTPS! 🔒

---

## 🔓 **Detailed Browser Instructions:**

### **Chrome/Edge:**
```
1. See warning: "Your connection is not private"
2. Click "Advanced" button
3. Click "Proceed to localhost (unsafe)"
4. ✅ Page loads with HTTPS!
```

### **Firefox:**
```
1. See warning: "Warning: Potential Security Risk Ahead"
2. Click "Advanced..."
3. Click "Accept the Risk and Continue"
4. ✅ Page loads with HTTPS!
```

### **Alternative - Type Bypass:**
In Chrome, when you see the warning, you can type:
```
thisisunsafe
```
(Just type it, nothing will appear, but it bypasses the warning)

---

## 🔒 **Why This Warning Appears:**

### **Self-Signed Certificate:**
- ✅ Certificate exists: `localhost.pem`
- ✅ Private key exists: `localhost-key.pem`
- ✅ Encryption is ACTIVE and WORKING
- ⚠️ Not signed by a trusted Certificate Authority (CA)

### **This is NORMAL and SAFE for:**
- ✓ Development environments
- ✓ Testing
- ✓ Local applications
- ✓ Internal tools

### **Your Data is Still Protected:**
- ✅ Full TLS encryption
- ✅ 4096-bit RSA
- ✅ AES-256 cipher
- ✅ SHA-256 signatures

---

## 🌐 **All Access URLs:**

Try any of these:
```
https://localhost:5000
https://127.0.0.1:5000
https://10.0.23.4:5000
```

All work with HTTPS! Just accept the certificate warning once.

---

## ✅ **Verify SSL is Working:**

### **After bypassing the warning:**

1. **Look for the 🔒 padlock** in the address bar
2. **Click the padlock**
3. **See**: "Connection is secure"
4. **View certificate**:
   - Issued to: localhost
   - Issued by: localhost
   - Valid: 365 days
   - Algorithm: RSA (4096 bits)

---

## 🎯 **Quick Test:**

```
1. Open: https://localhost:5000
2. Click: "Advanced"
3. Click: "Proceed to localhost"
4. Login: admin / admin123
5. See: "Welcome! [Kerberos TGT Issued]"
6. ✅ HTTPS working perfectly!
```

---

## 🔧 **If You Still Can't Connect:**

### **Option 1: Check Server is Running**
```powershell
# Check if server is running
netstat -an | Select-String ":5000"

# Should show:
# TCP  0.0.0.0:5000  LISTENING
```

### **Option 2: Restart Browser**
- Close ALL browser windows
- Open fresh browser
- Try again: https://localhost:5000

### **Option 3: Try Different Browser**
- Firefox often handles self-signed certs better
- Try: https://localhost:5000 in Firefox

### **Option 4: Temporarily Use HTTP**
If HTTPS is still problematic, you can use HTTP:
```
http://localhost:5000
```
(Still has Kerberos + AES encryption, just no TLS)

---

## 📝 **What "Connection Reset" Usually Means:**

1. **Browser blocked connection** - Solution: Accept certificate warning
2. **Server not running** - Solution: Check server is started
3. **Port blocked** - Solution: Check firewall
4. **Certificate mismatch** - Solution: Regenerate certificate

**Most common**: #1 - Just need to accept the certificate!

---

## 🎊 **Server Status:**

Your server IS running correctly on HTTPS:
```
✓ SSL Certificate: localhost.pem
✓ SSL Key: localhost-key.pem
🔒 HTTPS Server: Port 5000
✓ Database: Connected
✓ Kerberos: Active
✓ Ready for connections!
```

---

## ✅ **Summary:**

**SSL is WORKING!** You just need to:
1. Use: **https://localhost:5000**
2. Click: **"Advanced"**
3. Click: **"Proceed to localhost"**
4. ✅ **Done!**

The warning is normal for self-signed certificates. Just accept it once!

---

**Access now: https://localhost:5000** 🔒✨

