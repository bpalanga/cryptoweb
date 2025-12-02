# Credit Card Vault - Startup Guide

## ✅ All Issues Fixed!

The application is now **running successfully** with all errors resolved.

---

## 🚀 Quick Start

### Starting the Application

```powershell
# Navigate to the project directory
cd C:\Users\USER\Downloads\cryptoweb-main\cryptoweb-main

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the application
python app.py
```

### Access the Application

- **URL**: https://localhost:5000 (or http://localhost:5000 if no SSL)
- **Note**: If using HTTPS, you'll see a security warning - this is normal for self-signed certificates. Click "Advanced" → "Proceed anyway"

---

## 🔐 Default Login Credentials

| Role | User ID | Password | Access Level |
|------|---------|----------|--------------|
| **Admin** | admin | admin123 | Full system access |
| **Merchant** | merchant1 | merchant123 | Create invoices, view transactions |
| **Customer** | customer1 | customer123 | Manage cards, view invoices |
| **Auditor** | auditor1 | auditor123 | View logs and reports |

---

## 🛠️ Issues Fixed

### 1. **timedelta Import Error** ✅
- **Problem**: `PERMANENT_SESSION_LIFETIME` was set as integer instead of timedelta
- **Fix**: Added `timedelta` import and changed configuration to `timedelta(seconds=1800)`

### 2. **SSL Certificates** ✅
- **Problem**: SSL certificates were required but missing
- **Fix**: Made SSL optional for development mode
- **Status**: App now detects and uses SSL if available, otherwise runs in HTTP mode

### 3. **Database Setup** ✅
- **Problem**: Database and tables didn't exist
- **Fix**: Created `setup_database.py` script that:
  - Creates `credit_vault_db` database
  - Creates all required tables (Users, CardDetails, Invoices, AccessLogs)
  - Creates database views for reports
  - Adds default demo users

---

## 📁 Project Structure

```
cryptoweb-main/
├── app.py                  # Main Flask application
├── config.py               # Database configuration
├── setup_database.py       # Database initialization script (NEW)
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── login.html
│   ├── dashboard.html
│   ├── vault.html
│   └── ... (other templates)
└── venv/                   # Virtual environment
```

---

## 🔒 Security Features

- ✅ **AES-256 Encryption** - Credit card data encrypted at rest
- ✅ **SHA-256 Hashing** - Passwords securely hashed
- ✅ **Role-Based Access Control** - 4 user roles with different permissions
- ✅ **Audit Logging** - All actions tracked with IP and timestamp
- ✅ **SSL/HTTPS Support** - Secure transmission (when certificates present)
- ✅ **Session Management** - 30-minute timeout for security

---

## 📊 Database Schema

### Tables Created:
1. **Users** - User accounts with roles and credentials
2. **CardDetails** - Encrypted credit card information
3. **Invoices** - Payment transactions
4. **AccessLogs** - Security audit trail

### Views Created:
1. **UserRoleSummary** - User statistics by role
2. **CardStatistics** - Card usage analytics
3. **InvoiceSummary** - Invoice summaries
4. **SecurityAuditTrail** - Formatted audit logs

---

## 🎯 Key Features

### For Admins:
- View all users, cards, and invoices
- Register new users
- Access audit logs
- Full system reports

### For Merchants:
- Create invoices for customers
- View customer payment cards
- Track revenue and transactions

### For Customers:
- Add/manage credit cards
- View invoices
- Track spending

### For Auditors:
- View audit logs
- Access security reports
- Monitor system activity

---

## 🐛 Troubleshooting

### MySQL Connection Error
```
✗ Database Error: Can't connect to MySQL server
```
**Solution**: Make sure MySQL is running in XAMPP Control Panel

### Port Already in Use
```
OSError: [Errno 98] Address already in use
```
**Solution**: Kill existing Flask process or change port in `app.py`

### Module Not Found
```
ModuleNotFoundError: No module named 'flask'
```
**Solution**: 
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 📝 Notes

- **Development Mode**: Debug mode is enabled - DO NOT use in production
- **SSL Warning**: Self-signed certificates will show browser warnings
- **Database**: Uses local MySQL (XAMPP) with empty root password
- **Session Timeout**: Sessions expire after 30 minutes of inactivity

---

## 🔄 Resetting the Database

If you need to reset the database:

```powershell
.\venv\Scripts\Activate.ps1
python setup_database.py
```

This will recreate all tables and reset to default users.

---

## ✨ Status: READY TO USE!

Your Credit Card Vault application is fully configured and running! 🎉

