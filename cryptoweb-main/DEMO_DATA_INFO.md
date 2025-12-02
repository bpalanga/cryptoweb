# 🎭 Demo Data Information

## ✅ Database Now Contains Realistic Data!

Your Credit Card Vault application now has **real-looking people** with actual credit card information (test cards, not real ones).

---

## 👥 Demo Customers (8 People)

All customer passwords: **pass123**

| User ID | Name | Cards | Email |
|---------|------|-------|-------|
| `jsmith` | John Smith | 2 cards (Visa + Mastercard) | john.smith@email.com |
| `mjohnson` | Maria Johnson | 1 card (Amex) | maria.johnson@email.com |
| `rwilliams` | Robert Williams | 1 card (Discover) | robert.williams@email.com |
| `sbrown` | Sarah Brown | 1 card (Visa) | sarah.brown@email.com |
| `dmartinez` | David Martinez | 2 cards (Mastercard + Visa) | david.martinez@email.com |
| `lgarcia` | Lisa Garcia | 1 card (Amex) | lisa.garcia@email.com |
| `tanderson` | Thomas Anderson | 1 card (Discover) | thomas.anderson@email.com |
| `jthomas` | Jennifer Thomas | 1 card (Mastercard) | jennifer.thomas@email.com |

---

## 🏪 Demo Merchants (3 Stores)

All merchant passwords: **merchant123**

| User ID | Store Name | Email |
|---------|------------|-------|
| `amazon_store` | Amazon Online Store | billing@amazon-demo.com |
| `bestbuy_retail` | Best Buy Electronics | payments@bestbuy-demo.com |
| `walmart_shop` | Walmart Superstore | checkout@walmart-demo.com |

---

## 💳 Credit Card Details

### Sample Cards in the System:

**John Smith** (jsmith):
- Visa: `****0366` - Expires 12/2026
- Mastercard: `****9903` - Expires 08/2027
- Address: 123 Main Street, New York, NY 10001

**Maria Johnson** (mjohnson):
- Amex: `****0005` - Expires 03/2028
- Address: 456 Oak Avenue, Los Angeles, CA 90001

**David Martinez** (dmartinez):
- Mastercard: `****4444` - Expires 11/2025
- Visa: `****1881` - Expires 05/2026
- Address: 567 Maple Drive, Phoenix, AZ 85001

... and 5 more customers with their cards!

---

## 📊 Database Statistics

- **Total Customers**: 9 (1 original + 8 new)
- **Total Credit Cards**: 20 (encrypted with AES-256)
- **Total Invoices**: 20+ transactions
- **Total Merchants**: 4 (1 original + 3 new)
- **Card Types**: Visa, Mastercard, Amex, Discover

---

## 🔐 Login Instructions

### To View All Cards (Admin):

1. Go to: **http://localhost:5000**
2. Login with:
   - **User ID**: `admin`
   - **Password**: `admin123`
3. Click **"Vault"** in the navigation
4. You'll see **all 20 credit cards** from all customers!

### To View Your Own Cards (Customer):

1. Go to: **http://localhost:5000**
2. Login as any customer (e.g., `jsmith` / `pass123`)
3. Click **"Vault"** to see only your cards
4. Click **"Dashboard"** to see your statistics

### To View Customer Cards (Merchant):

1. Go to: **http://localhost:5000**
2. Login as merchant (e.g., `amazon_store` / `merchant123`)
3. Create invoices for customers
4. View cards used in your transactions

---

## 🎯 What You'll See as Admin:

When you login as **admin** and go to the **Vault**, you'll see:

```
Card Vault - admin

Stored Cards:

ID  | User      | Full Name         | Card Number | Card Type  | Billing Address
----|-----------|-------------------|-------------|------------|------------------
1   | jsmith    | John Smith        | ****0366    | visa       | 123 Main Street, NY
2   | jsmith    | John Smith        | ****9903    | mastercard | 123 Main Street, NY
3   | mjohnson  | Maria Johnson     | ****0005    | amex       | 456 Oak Avenue, LA
4   | rwilliams | Robert Williams   | ****1117    | discover   | 789 Pine Road, Chicago
...and 16 more cards!
```

---

## 💰 Invoices/Transactions

The system also created **20 realistic invoices** showing:
- Purchases from different merchants
- Various amounts ($15.99 - $999.99)
- Different statuses (paid, pending, failed)
- Dates over the last 90 days

---

## 🔒 Security Features Still Active

✅ All credit card numbers are **AES-256 encrypted** in the database
✅ All CVVs are **encrypted**
✅ All passwords are **SHA-256 hashed**
✅ Role-based access control is **enforced**
✅ All actions are **logged** in AccessLogs table

---

## 🚀 Quick Access URLs

- **Main Login**: http://localhost:5000
- **Test Page**: http://localhost:5000/test (verify server is running)
- **Health Check**: http://localhost:5000/health (JSON API)

---

## 📝 Notes

- **Test Card Numbers**: These are industry-standard test card numbers used for development
- **Not Real**: All names, addresses, and card data are fictional
- **Safe to Use**: Perfect for demonstrations and testing
- **Data Persistence**: This data will remain until you reset the database

---

## 🔄 To Reset/Regenerate Data

If you want to start fresh:

```powershell
cd C:\Users\USER\Downloads\cryptoweb-main\cryptoweb-main
.\venv\Scripts\Activate.ps1
python setup_database.py        # Reset database
python populate_demo_data.py    # Add demo data again
```

---

## ✨ Enjoy Your Populated Database!

Now when you login as **admin** and view the **Card Vault**, you'll see **real-looking data** instead of empty pages! 🎉

