#!/usr/bin/env python3
"""
Database Setup Script for Credit Card Vault
Creates database and all required tables
"""

import mysql.connector
from mysql.connector import Error

def setup_database():
    """Create database and tables"""
    
    # Connect without database first
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = conn.cursor()
        
        # Create database
        print("Creating database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS credit_vault_db")
        cursor.execute("USE credit_vault_db")
        print("✓ Database created/exists")
        
        # Create Users table
        print("Creating Users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                userid VARCHAR(50) PRIMARY KEY,
                password_hash VARCHAR(64) NOT NULL,
                role ENUM('admin', 'merchant', 'customer', 'auditor') DEFAULT 'customer',
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                phone VARCHAR(20),
                last_login TIMESTAMP NULL,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        print("✓ Users table created")
        
        # Create CardDetails table
        print("Creating CardDetails table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CardDetails (
                id INT AUTO_INCREMENT PRIMARY KEY,
                userid VARCHAR(50) NOT NULL,
                card_number VARBINARY(255) NOT NULL,
                cvv VARBINARY(255) NOT NULL,
                card_holder_name VARCHAR(100) NOT NULL,
                expiry_month VARCHAR(2) NOT NULL,
                expiry_year VARCHAR(4) NOT NULL,
                billing_address TEXT NOT NULL,
                card_type ENUM('visa', 'mastercard', 'amex', 'discover') DEFAULT 'visa',
                is_default BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (userid) REFERENCES Users(userid) ON DELETE CASCADE
            )
        """)
        print("✓ CardDetails table created")
        
        # Create Invoices table
        print("Creating Invoices table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Invoices (
                invoice_id INT AUTO_INCREMENT PRIMARY KEY,
                merchant_id VARCHAR(50) NOT NULL,
                customer_id VARCHAR(50) NOT NULL,
                card_id INT,
                amount DECIMAL(10,2) NOT NULL,
                description TEXT,
                status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
                invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (merchant_id) REFERENCES Users(userid),
                FOREIGN KEY (customer_id) REFERENCES Users(userid),
                FOREIGN KEY (card_id) REFERENCES CardDetails(id)
            )
        """)
        print("✓ Invoices table created")
        
        # Create AccessLogs table
        print("Creating AccessLogs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AccessLogs (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                userid VARCHAR(50),
                action VARCHAR(100) NOT NULL,
                table_name VARCHAR(50),
                record_id INT,
                ip_address VARCHAR(45),
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (userid) REFERENCES Users(userid) ON DELETE SET NULL
            )
        """)
        print("✓ AccessLogs table created")
        
        # Create Views
        print("Creating database views...")
        
        # UserRoleSummary view
        cursor.execute("""
            CREATE OR REPLACE VIEW UserRoleSummary AS
            SELECT 
                role,
                COUNT(*) as user_count,
                SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) as active_users
            FROM Users
            GROUP BY role
        """)
        
        # CardStatistics view
        cursor.execute("""
            CREATE OR REPLACE VIEW CardStatistics AS
            SELECT 
                card_type,
                COUNT(*) as card_count,
                COUNT(DISTINCT userid) as unique_users
            FROM CardDetails
            WHERE is_active = TRUE
            GROUP BY card_type
        """)
        
        # InvoiceSummary view
        cursor.execute("""
            CREATE OR REPLACE VIEW InvoiceSummary AS
            SELECT 
                status,
                COUNT(*) as invoice_count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount
            FROM Invoices
            GROUP BY status
        """)
        
        # SecurityAuditTrail view
        cursor.execute("""
            CREATE OR REPLACE VIEW SecurityAuditTrail AS
            SELECT 
                al.log_id,
                al.userid,
                u.role,
                u.full_name,
                al.action,
                al.table_name,
                al.record_id,
                al.ip_address,
                al.timestamp
            FROM AccessLogs al
            LEFT JOIN Users u ON al.userid = u.userid
            ORDER BY al.timestamp DESC
        """)
        print("✓ Database views created")
        
        # Check if default users exist
        cursor.execute("SELECT COUNT(*) FROM Users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print("\nCreating default users...")
            
            # Create default admin
            cursor.execute("""
                INSERT INTO Users (userid, password_hash, role, full_name, email)
                VALUES ('admin', SHA2('admin123', 256), 'admin', 'System Administrator', 'admin@cardvault.com')
            """)
            print("✓ Admin user created (userid: admin, password: admin123)")
            
            # Create demo merchant
            cursor.execute("""
                INSERT INTO Users (userid, password_hash, role, full_name, email)
                VALUES ('merchant1', SHA2('merchant123', 256), 'merchant', 'Demo Merchant', 'merchant@demo.com')
            """)
            print("✓ Merchant user created (userid: merchant1, password: merchant123)")
            
            # Create demo customer
            cursor.execute("""
                INSERT INTO Users (userid, password_hash, role, full_name, email)
                VALUES ('customer1', SHA2('customer123', 256), 'customer', 'Demo Customer', 'customer@demo.com')
            """)
            print("✓ Customer user created (userid: customer1, password: customer123)")
            
            # Create demo auditor
            cursor.execute("""
                INSERT INTO Users (userid, password_hash, role, full_name, email)
                VALUES ('auditor1', SHA2('auditor123', 256), 'auditor', 'Demo Auditor', 'auditor@demo.com')
            """)
            print("✓ Auditor user created (userid: auditor1, password: auditor123)")
        else:
            print(f"\n✓ Database already has {user_count} users")
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 70)
        print("DATABASE SETUP COMPLETE!")
        print("=" * 70)
        print("\nDefault Login Credentials:")
        print("  Admin:    userid=admin,     password=admin123")
        print("  Merchant: userid=merchant1, password=merchant123")
        print("  Customer: userid=customer1, password=customer123")
        print("  Auditor:  userid=auditor1,  password=auditor123")
        print("=" * 70)
        
        return True
        
    except Error as e:
        print(f"✗ Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    setup_database()

