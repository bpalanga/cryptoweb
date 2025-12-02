#!/usr/bin/env python3
"""
Populate Database with Realistic Demo Data
Creates realistic users, credit cards, and invoices for demonstration
"""

import mysql.connector
from datetime import datetime, timedelta
import random

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'credit_vault_db',
    'charset': 'utf8mb4'
}

# AES Encryption Key (same as in app.py)
AES_KEY = "my-secure-aes-key-2024"

# Realistic demo data
DEMO_CUSTOMERS = [
    {
        'userid': 'jsmith',
        'password': 'pass123',
        'full_name': 'John Smith',
        'email': 'john.smith@email.com',
        'cards': [
            {
                'card_number': '4532015112830366',  # Visa test card
                'cvv': '123',
                'holder': 'JOHN SMITH',
                'exp_month': '12',
                'exp_year': '2026',
                'address': '123 Main Street, New York, NY 10001',
                'card_type': 'visa',
                'is_default': True
            },
            {
                'card_number': '5425233430109903',  # Mastercard test card
                'cvv': '456',
                'holder': 'JOHN SMITH',
                'exp_month': '08',
                'exp_year': '2027',
                'address': '123 Main Street, New York, NY 10001',
                'card_type': 'mastercard',
                'is_default': False
            }
        ]
    },
    {
        'userid': 'mjohnson',
        'password': 'pass123',
        'full_name': 'Maria Johnson',
        'email': 'maria.johnson@email.com',
        'cards': [
            {
                'card_number': '378282246310005',  # Amex test card
                'cvv': '7890',
                'holder': 'MARIA JOHNSON',
                'exp_month': '03',
                'exp_year': '2028',
                'address': '456 Oak Avenue, Los Angeles, CA 90001',
                'card_type': 'amex',
                'is_default': True
            }
        ]
    },
    {
        'userid': 'rwilliams',
        'password': 'pass123',
        'full_name': 'Robert Williams',
        'email': 'robert.williams@email.com',
        'cards': [
            {
                'card_number': '6011111111111117',  # Discover test card
                'cvv': '321',
                'holder': 'ROBERT WILLIAMS',
                'exp_month': '06',
                'exp_year': '2026',
                'address': '789 Pine Road, Chicago, IL 60601',
                'card_type': 'discover',
                'is_default': True
            }
        ]
    },
    {
        'userid': 'sbrown',
        'password': 'pass123',
        'full_name': 'Sarah Brown',
        'email': 'sarah.brown@email.com',
        'cards': [
            {
                'card_number': '4111111111111111',  # Visa test card
                'cvv': '789',
                'holder': 'SARAH BROWN',
                'exp_month': '09',
                'exp_year': '2027',
                'address': '321 Elm Street, Houston, TX 77001',
                'card_type': 'visa',
                'is_default': True
            }
        ]
    },
    {
        'userid': 'dmartinez',
        'password': 'pass123',
        'full_name': 'David Martinez',
        'email': 'david.martinez@email.com',
        'cards': [
            {
                'card_number': '5555555555554444',  # Mastercard test card
                'cvv': '654',
                'holder': 'DAVID MARTINEZ',
                'exp_month': '11',
                'exp_year': '2025',
                'address': '567 Maple Drive, Phoenix, AZ 85001',
                'card_type': 'mastercard',
                'is_default': True
            },
            {
                'card_number': '4012888888881881',  # Visa test card
                'cvv': '147',
                'holder': 'DAVID MARTINEZ',
                'exp_month': '05',
                'exp_year': '2026',
                'address': '567 Maple Drive, Phoenix, AZ 85001',
                'card_type': 'visa',
                'is_default': False
            }
        ]
    },
    {
        'userid': 'lgarcia',
        'password': 'pass123',
        'full_name': 'Lisa Garcia',
        'email': 'lisa.garcia@email.com',
        'cards': [
            {
                'card_number': '371449635398431',  # Amex test card
                'cvv': '9876',
                'holder': 'LISA GARCIA',
                'exp_month': '04',
                'exp_year': '2028',
                'address': '890 Cedar Lane, Philadelphia, PA 19101',
                'card_type': 'amex',
                'is_default': True
            }
        ]
    },
    {
        'userid': 'tanderson',
        'password': 'pass123',
        'full_name': 'Thomas Anderson',
        'email': 'thomas.anderson@email.com',
        'cards': [
            {
                'card_number': '6011000990139424',  # Discover test card
                'cvv': '258',
                'holder': 'THOMAS ANDERSON',
                'exp_month': '07',
                'exp_year': '2027',
                'address': '234 Birch Street, San Antonio, TX 78201',
                'card_type': 'discover',
                'is_default': True
            }
        ]
    },
    {
        'userid': 'jthomas',
        'password': 'pass123',
        'full_name': 'Jennifer Thomas',
        'email': 'jennifer.thomas@email.com',
        'cards': [
            {
                'card_number': '5105105105105100',  # Mastercard test card
                'cvv': '369',
                'holder': 'JENNIFER THOMAS',
                'exp_month': '10',
                'exp_year': '2026',
                'address': '678 Walnut Avenue, San Diego, CA 92101',
                'card_type': 'mastercard',
                'is_default': True
            }
        ]
    }
]

DEMO_MERCHANTS = [
    {
        'userid': 'amazon_store',
        'password': 'merchant123',
        'full_name': 'Amazon Online Store',
        'email': 'billing@amazon-demo.com'
    },
    {
        'userid': 'bestbuy_retail',
        'password': 'merchant123',
        'full_name': 'Best Buy Electronics',
        'email': 'payments@bestbuy-demo.com'
    },
    {
        'userid': 'walmart_shop',
        'password': 'merchant123',
        'full_name': 'Walmart Superstore',
        'email': 'checkout@walmart-demo.com'
    }
]

# Invoice descriptions for realism
INVOICE_DESCRIPTIONS = [
    "Wireless Bluetooth Headphones - Premium Sound Quality",
    "4K Smart TV 55 inch - Samsung QLED",
    "Laptop Computer - Dell XPS 15",
    "Grocery Shopping - Weekly Essentials",
    "Smartphone - iPhone 14 Pro",
    "Gaming Console - PlayStation 5",
    "Kitchen Appliance Set",
    "Office Supplies Bundle",
    "Fitness Tracker Watch",
    "Home Security Camera System",
    "Electric Toothbrush Set",
    "Coffee Maker - Espresso Machine",
    "Running Shoes - Nike Air",
    "Dining Table Set - 6 Seater",
    "Wireless Router - WiFi 6",
    "Outdoor Furniture Set",
    "Book Collection - Best Sellers",
    "Garden Tools Kit",
    "Air Purifier - HEPA Filter",
    "Bluetooth Speaker - Portable"
]

def populate_database():
    """Populate database with realistic demo data"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("=" * 70)
        print("POPULATING DATABASE WITH DEMO DATA")
        print("=" * 70)
        
        # 1. Add demo customers
        print("\n1. Adding demo customers...")
        customer_count = 0
        for customer in DEMO_CUSTOMERS:
            try:
                cursor.execute("""
                    INSERT INTO Users (userid, password_hash, role, full_name, email, is_active)
                    VALUES (%s, SHA2(%s, 256), 'customer', %s, %s, TRUE)
                """, (customer['userid'], customer['password'], 
                      customer['full_name'], customer['email']))
                customer_count += 1
                print(f"   ✓ Added customer: {customer['full_name']} (userid: {customer['userid']})")
            except mysql.connector.IntegrityError:
                print(f"   ⚠ Customer {customer['userid']} already exists, skipping...")
        
        conn.commit()
        print(f"\n   Total new customers added: {customer_count}")
        
        # 2. Add demo merchants
        print("\n2. Adding demo merchants...")
        merchant_count = 0
        for merchant in DEMO_MERCHANTS:
            try:
                cursor.execute("""
                    INSERT INTO Users (userid, password_hash, role, full_name, email, is_active)
                    VALUES (%s, SHA2(%s, 256), 'merchant', %s, %s, TRUE)
                """, (merchant['userid'], merchant['password'],
                      merchant['full_name'], merchant['email']))
                merchant_count += 1
                print(f"   ✓ Added merchant: {merchant['full_name']}")
            except mysql.connector.IntegrityError:
                print(f"   ⚠ Merchant {merchant['userid']} already exists, skipping...")
        
        conn.commit()
        print(f"\n   Total new merchants added: {merchant_count}")
        
        # 3. Add credit cards for customers
        print("\n3. Adding credit cards (AES encrypted)...")
        card_count = 0
        card_ids = []
        for customer in DEMO_CUSTOMERS:
            for card in customer['cards']:
                try:
                    cursor.execute("""
                        INSERT INTO CardDetails 
                        (userid, card_number, cvv, card_holder_name, expiry_month, 
                         expiry_year, billing_address, card_type, is_default)
                        VALUES (%s, AES_ENCRYPT(%s, %s), AES_ENCRYPT(%s, %s), 
                                %s, %s, %s, %s, %s, %s)
                    """, (customer['userid'], card['card_number'], AES_KEY,
                          card['cvv'], AES_KEY, card['holder'], 
                          card['exp_month'], card['exp_year'],
                          card['address'], card['card_type'], card['is_default']))
                    card_id = cursor.lastrowid
                    card_ids.append((card_id, customer['userid']))
                    card_count += 1
                    print(f"   ✓ Added {card['card_type'].upper()} card for {customer['full_name']}")
                except Exception as e:
                    print(f"   ⚠ Error adding card: {e}")
        
        conn.commit()
        print(f"\n   Total cards added: {card_count}")
        
        # 4. Create realistic invoices
        print("\n4. Creating invoices...")
        invoice_count = 0
        
        # Get all merchant IDs
        cursor.execute("SELECT userid FROM Users WHERE role = 'merchant'")
        merchants = [row[0] for row in cursor.fetchall()]
        
        if merchants and card_ids:
            # Create 20-30 invoices with realistic data
            num_invoices = random.randint(20, 30)
            statuses = ['paid', 'paid', 'paid', 'paid', 'pending', 'pending', 'failed']
            
            for i in range(num_invoices):
                merchant_id = random.choice(merchants)
                card_id, customer_id = random.choice(card_ids)
                amount = round(random.uniform(15.99, 999.99), 2)
                description = random.choice(INVOICE_DESCRIPTIONS)
                status = random.choice(statuses)
                
                # Random date within last 90 days
                days_ago = random.randint(0, 90)
                invoice_date = datetime.now() - timedelta(days=days_ago)
                
                try:
                    cursor.execute("""
                        INSERT INTO Invoices 
                        (merchant_id, customer_id, card_id, amount, status, invoice_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (merchant_id, customer_id, card_id, amount, status, invoice_date))
                    invoice_count += 1
                except Exception as e:
                    print(f"   ⚠ Error creating invoice: {e}")
            
            conn.commit()
            print(f"   ✓ Created {invoice_count} invoices")
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("DATABASE POPULATED SUCCESSFULLY!")
        print("=" * 70)
        print("\n📊 Summary:")
        print(f"   • {customer_count} new customers")
        print(f"   • {merchant_count} new merchants")
        print(f"   • {card_count} credit cards (encrypted)")
        print(f"   • {invoice_count} invoices/transactions")
        print("\n🔐 Login Credentials:")
        print("\n   ADMIN:")
        print("   • userid: admin, password: admin123")
        print("\n   DEMO CUSTOMERS (all use password: pass123):")
        for customer in DEMO_CUSTOMERS[:5]:  # Show first 5
            print(f"   • userid: {customer['userid']:<12} - {customer['full_name']}")
        print(f"   • ... and {len(DEMO_CUSTOMERS) - 5} more customers")
        print("\n   DEMO MERCHANTS (all use password: merchant123):")
        for merchant in DEMO_MERCHANTS:
            print(f"   • userid: {merchant['userid']:<15} - {merchant['full_name']}")
        print("\n" + "=" * 70)
        print("✅ Login as 'admin' to view all cards in the vault!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

if __name__ == '__main__':
    populate_database()

