# app.py - Credit Card Vault Application with Kerberos Security
from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import mysql.connector
from functools import wraps
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import current_app # Import current_app

# Import Kerberos authentication module
from kerberos_auth import (
    KerberosAuth, KerberosTicket, KerberosLogger,
    kerberos_required, kerberos_role_required, get_ticket_info
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "credit-vault-secret-key-2024")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=1800)

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'credit_vault_db',
    'charset': 'utf8mb4'
}

# AES Encryption Key for sensitive data
AES_KEY = os.getenv("AES_KEY", "my-secure-aes-key-2024")

# ==================== DATABASE FUNCTIONS ====================
def get_db():
    """Create database connection"""
    return mysql.connector.connect(**db_config)

def log_access(action, table_name=None, record_id=None):
    """Log user actions"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO AccessLogs (userid, action, table_name, record_id, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session.get('userid'), action, table_name, record_id,
              request.remote_addr, request.headers.get('User-Agent')))
        conn.commit()
        conn.close()
    except Exception as e:
        app.logger.error(f"Log error: {e}")

# ==================== DECORATORS ====================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'userid' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'userid' not in session:
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('Access denied. Insufficient privileges.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ==================== AUTHENTICATION ====================
@app.route('/', methods=['GET', 'POST'])
def login():
    """Login with SHA-256 password hashing"""
    if request.method == 'POST':
        userid = request.form.get('userid', '').strip()
        password = request.form.get('password', '')
        
        if not userid or not password:
            flash('User ID and password required.', 'danger')
            return render_template('login.html')
        
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT userid, role, full_name, is_active 
                FROM Users 
                WHERE userid = %s AND password_hash = SHA2(%s, 256)
            """, (userid, password))
            
            user = cursor.fetchone()
            
            if user and user['is_active']:
                cursor.execute("UPDATE Users SET last_login = NOW() WHERE userid = %s", (userid,))
                conn.commit()
                conn.close()
                
                # Standard session authentication
                session['userid'] = user['userid']
                session['role'] = user['role']
                session['full_name'] = user['full_name']
                session.permanent = True
                
                # Issue Kerberos TGT (Ticket Granting Ticket)
                ticket, msg = KerberosAuth.authenticate(userid, password, db_config)
                if ticket:
                    session['kerberos_ticket'] = ticket
                    session['kerberos_enabled'] = True
                    KerberosLogger.log_event('TGT_ISSUED', userid, msg, db_config)
                    flash(f'Welcome, {user["full_name"]}! [Kerberos TGT Issued]', 'success')
                else:
                    flash(f'Welcome, {user["full_name"]}! (Kerberos: {msg})', 'warning')
                
                log_access('LOGIN_SUCCESS')
                return redirect(url_for('dashboard'))
            else:
                log_access('LOGIN_FAILED')
                KerberosLogger.log_event('AUTH_FAILED', userid, 'Invalid credentials', db_config)
                flash('Invalid credentials or account disabled.', 'danger')
                conn.close()
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def register():
    """Register new user (Admin only)"""
    if request.method == 'POST':
        userid = request.form.get('userid', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'customer')
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        
        if not all([userid, password, full_name, email]) or len(password) < 8:
            flash('All fields required. Password must be 8+ characters.', 'danger')
            return render_template('register.html')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO Users (userid, password_hash, role, full_name, email, is_active)
                VALUES (%s, SHA2(%s, 256), %s, %s, %s, TRUE)
            """, (userid, password, role, full_name, email))
            
            conn.commit()
            conn.close()
            
            log_access('REGISTER_USER', 'Users')
            flash(f'User {userid} registered successfully!', 'success')
            return redirect(url_for('dashboard'))
        except mysql.connector.IntegrityError:
            flash('User ID or email already exists.', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    if 'userid' in session:
        log_access('LOGOUT')
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# ==================== DASHBOARD ====================
@app.route('/dashboard')
@login_required
def dashboard():
    """Role-based dashboard"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    stats = {}
    role = session['role']
    
    if role == 'admin':
        cursor.execute("SELECT COUNT(*) as total_users FROM Users")
        stats['total_users'] = cursor.fetchone()['total_users']
        
        cursor.execute("SELECT COUNT(*) as total_cards FROM CardDetails WHERE is_active = TRUE")
        stats['total_cards'] = cursor.fetchone()['total_cards']
        
        cursor.execute("SELECT COUNT(*) as total_invoices FROM Invoices")
        stats['total_invoices'] = cursor.fetchone()['total_invoices']
        
        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total_revenue FROM Invoices WHERE status = 'paid'")
        stats['total_revenue'] = cursor.fetchone()['total_revenue']
        
    elif role == 'merchant':
        cursor.execute("""
            SELECT 
                COUNT(*) as total_invoices,
                COALESCE(SUM(amount), 0) as total_revenue,
                COALESCE(AVG(amount), 0) as avg_invoice,
                COUNT(DISTINCT customer_id) as unique_customers
            FROM Invoices WHERE merchant_id = %s
        """, (session['userid'],))
        stats = cursor.fetchone()
        
    elif role == 'customer':
        cursor.execute("""
            SELECT 
                COUNT(*) as my_cards,
                COUNT(DISTINCT i.merchant_id) as merchants_used,
                COALESCE(SUM(i.amount), 0) as total_spent
            FROM CardDetails cd
            LEFT JOIN Invoices i ON cd.id = i.card_id
            WHERE cd.userid = %s AND cd.is_active = TRUE
        """, (session['userid'],))
        stats = cursor.fetchone()
    
    elif role == 'auditor':
        cursor.execute("SELECT COUNT(*) as recent_logs FROM AccessLogs WHERE timestamp > DATE_SUB(NOW(), INTERVAL 7 DAY)")
        stats['recent_logs'] = cursor.fetchone()['recent_logs']
        
        cursor.execute("SELECT COUNT(DISTINCT userid) as active_users FROM AccessLogs WHERE timestamp > DATE_SUB(NOW(), INTERVAL 1 DAY)")
        stats['active_users'] = cursor.fetchone()['active_users']
    
    conn.close()
    log_access('VIEW_DASHBOARD')
    return render_template('dashboard.html', stats=stats, role=role)

# ==================== CARD VAULT ====================
@app.route('/vault')
@login_required
@role_required('admin', 'merchant', 'customer')
def vault():
    """View stored cards with AES decryption"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    role = session['role']
    userid = session['userid']
    
    if role == 'admin':
        cursor.execute("""
            SELECT 
                cd.id,
                cd.userid,
                u.full_name,
                CONCAT('****', RIGHT(AES_DECRYPT(cd.card_number, %s), 4)) as masked_card,
                cd.card_type,
                cd.billing_address,
                cd.is_default,
                cd.created_at
            FROM CardDetails cd
            JOIN Users u ON cd.userid = u.userid
            WHERE cd.is_active = TRUE
            ORDER BY cd.created_at DESC
        """, (AES_KEY,))
        
    elif role == 'merchant':
        cursor.execute("""
            SELECT DISTINCT
                cd.id,
                cd.userid,
                u.full_name,
                CONCAT('****', RIGHT(AES_DECRYPT(cd.card_number, %s), 4)) as masked_card,
                cd.card_type,
                COUNT(i.invoice_id) as invoice_count
            FROM CardDetails cd
            JOIN Users u ON cd.userid = u.userid
            JOIN Invoices i ON cd.id = i.card_id
            WHERE cd.is_active = TRUE AND i.merchant_id = %s
            GROUP BY cd.id
            ORDER BY cd.created_at DESC
        """, (AES_KEY, userid))
        
    else:  # customer
        cursor.execute("""
            SELECT 
                id,
                userid,
                CONCAT('****', RIGHT(AES_DECRYPT(card_number, %s), 4)) as masked_card,
                card_type,
                billing_address,
                is_default,
                created_at
            FROM CardDetails
            WHERE userid = %s AND is_active = TRUE
            ORDER BY is_default DESC, created_at DESC
        """, (AES_KEY, userid))
    
    cards = cursor.fetchall()
    conn.close()
    
    log_access('VIEW_VAULT')
    return render_template('vault.html', cards=cards, role=role)

@app.route('/add-card', methods=['GET', 'POST'])
@login_required
@role_required('customer', 'admin')
def add_card():
    """Add new card with AES encryption"""
    if request.method == 'POST':
        card_number = request.form.get('card_number', '').replace(' ', '')
        cvv = request.form.get('cvv', '')
        holder = request.form.get('card_holder', '').strip().upper()
        exp_month = request.form.get('expiry_month', '')
        exp_year = request.form.get('expiry_year', '')
        address = request.form.get('billing_address', '').strip()
        card_type = request.form.get('card_type', 'visa')
        
        # Validation
        if not all([card_number, cvv, holder, exp_month, exp_year, address]):
            flash('All fields required.', 'danger')
            return render_template('add_card.html', current_year=datetime.now().year)
        
        if not (13 <= len(card_number) <= 19 and card_number.isdigit()):
            flash('Invalid card number.', 'danger')
            return render_template('add_card.html', current_year=datetime.now().year)
        
        if not (cvv.isdigit() and 3 <= len(cvv) <= 4):
            flash('Invalid CVV.', 'danger')
            return render_template('add_card.html', current_year=datetime.now().year)
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Check if first card (set as default)
            cursor.execute("SELECT COUNT(*) FROM CardDetails WHERE userid = %s AND is_active = TRUE", 
                          (session['userid'],))
            is_default = cursor.fetchone()[0] == 0
            
            # Insert with AES encryption
            cursor.execute("""
                INSERT INTO CardDetails 
                (userid, card_number, cvv, card_holder_name, expiry_month, expiry_year, 
                 billing_address, card_type, is_default)
                VALUES (%s, AES_ENCRYPT(%s, %s), AES_ENCRYPT(%s, %s), %s, %s, %s, %s, %s, %s)
            """, (session['userid'], card_number, AES_KEY, cvv, AES_KEY, 
                  holder, exp_month, exp_year, address, card_type, is_default))
            
            conn.commit()
            card_id = cursor.lastrowid
            conn.close()
            
            log_access('ADD_CARD', 'CardDetails', card_id)
            flash('Card added successfully!', 'success')
            return redirect(url_for('vault'))
            
        except mysql.connector.IntegrityError:
            flash('Card already registered.', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('add_card.html', current_year=datetime.now().year)

@app.route('/card-details/<int:card_id>')
@login_required
@role_required('admin', 'merchant')
def card_details(card_id):
    """View full card details with AES decryption"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    role = session['role']
    userid = session['userid']
    
    # Permission check for merchant
    if role == 'merchant':
        cursor.execute("""
            SELECT 1 FROM Invoices i
            JOIN CardDetails cd ON i.card_id = cd.id
            WHERE cd.id = %s AND i.merchant_id = %s LIMIT 1
        """, (card_id, userid))
        if not cursor.fetchone():
            conn.close()
            flash('Access denied.', 'danger')
            return redirect(url_for('vault'))
    
    # Get decrypted card details
    cursor.execute("""
        SELECT 
            AES_DECRYPT(cd.card_number, %s) as card_number,
            AES_DECRYPT(cd.cvv, %s) as cvv,
            cd.card_holder_name,
            cd.expiry_month,
            cd.expiry_year,
            cd.billing_address,
            cd.card_type,
            u.full_name
        FROM CardDetails cd
        JOIN Users u ON cd.userid = u.userid
        WHERE cd.id = %s
    """, (AES_KEY, AES_KEY, card_id))
    
    card = cursor.fetchone()
    conn.close()
    
    if card:
        # Mask for display
        card_display = {
            'card_number': f"****{card['card_number'][-4:]}",
            'cvv': '***',
            'card_holder_name': card['card_holder_name'],
            'expiry_month': card['expiry_month'],
            'expiry_year': card['expiry_year'],
            'billing_address': card['billing_address'],
            'card_type': card['card_type'],
            'full_name': card['full_name']
        }
        
        log_access('VIEW_CARD_DETAILS', 'CardDetails', card_id)
        return render_template('card_details.html', card=card_display, card_id=card_id)
    
    flash('Card not found.', 'danger')
    return redirect(url_for('vault'))

@app.route('/delete-card/<int:card_id>', methods=['POST'])
@login_required
@role_required('admin', 'customer')
def delete_card(card_id):
    """Soft delete card"""
    conn = get_db()
    cursor = conn.cursor()
    
    if session['role'] != 'admin':
        cursor.execute("SELECT userid FROM CardDetails WHERE id = %s", (card_id,))
        card = cursor.fetchone()
        if not card or card[0] != session['userid']:
            conn.close()
            flash('Access denied.', 'danger')
            return redirect(url_for('vault'))
    
    cursor.execute("UPDATE CardDetails SET is_active = FALSE WHERE id = %s", (card_id,))
    conn.commit()
    conn.close()
    
    log_access('DELETE_CARD', 'CardDetails', card_id)
    flash('Card deleted successfully.', 'success')
    return redirect(url_for('vault'))

# ==================== INVOICES ====================
@app.route('/invoices')
@login_required
def invoices():
    """View invoices"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    role = session['role']
    userid = session['userid']
    
    if role == 'admin':
        cursor.execute("""
            SELECT i.*, 
                   m.full_name as merchant_name,
                   c.full_name as customer_name,
                   CONCAT('****', RIGHT(AES_DECRYPT(cd.card_number, %s), 4)) as masked_card
            FROM Invoices i
            JOIN Users m ON i.merchant_id = m.userid
            JOIN Users c ON i.customer_id = c.userid
            LEFT JOIN CardDetails cd ON i.card_id = cd.id
            ORDER BY i.invoice_date DESC
        """, (AES_KEY,))
        
    elif role == 'merchant':
        cursor.execute("""
            SELECT i.*, 
                   c.full_name as customer_name,
                   CONCAT('****', RIGHT(AES_DECRYPT(cd.card_number, %s), 4)) as masked_card
            FROM Invoices i
            JOIN Users c ON i.customer_id = c.userid
            LEFT JOIN CardDetails cd ON i.card_id = cd.id
            WHERE i.merchant_id = %s
            ORDER BY i.invoice_date DESC
        """, (AES_KEY, userid))
        
    else:  # customer
        cursor.execute("""
            SELECT i.*, 
                   m.full_name as merchant_name,
                   CONCAT('****', RIGHT(AES_DECRYPT(cd.card_number, %s), 4)) as masked_card
            FROM Invoices i
            JOIN Users m ON i.merchant_id = m.userid
            LEFT JOIN CardDetails cd ON i.card_id = cd.id
            WHERE i.customer_id = %s
            ORDER BY i.invoice_date DESC
        """, (AES_KEY, userid))
    
    invoice_list = cursor.fetchall()
    conn.close()
    
    log_access('VIEW_INVOICES')
    return render_template('invoices.html', invoices=invoice_list, role=role)

@app.route('/create-invoice', methods=['GET', 'POST'])
@login_required
@role_required('merchant', 'admin')
def create_invoice():
    """Create invoice using stored card"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        card_id = request.form.get('card_id')
        amount = request.form.get('amount')
        description = request.form.get('description', '')
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be positive.', 'danger')
                return redirect(url_for('create_invoice'))
            
            # Verify card ownership
            cursor.execute("SELECT userid FROM CardDetails WHERE id = %s", (card_id,))
            card = cursor.fetchone()
            
            if not card or card['userid'] != customer_id:
                flash('Invalid card selection.', 'danger')
                return redirect(url_for('create_invoice'))
            
            # Create invoice (description field removed - table doesn't have it)
            cursor.execute("""
                INSERT INTO Invoices (merchant_id, customer_id, card_id, amount)
                VALUES (%s, %s, %s, %s)
            """, (session['userid'], customer_id, card_id, amount))
            
            conn.commit()
            invoice_id = cursor.lastrowid
            
            log_access('CREATE_INVOICE', 'Invoices', invoice_id)
            flash(f'Invoice #{invoice_id} created!', 'success')
            return redirect(url_for('invoices'))
            
        except ValueError:
            flash('Invalid amount.', 'danger')
        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    # Get customers
    cursor.execute("""
        SELECT userid, full_name 
        FROM Users 
        WHERE role = 'customer' AND is_active = TRUE
        ORDER BY full_name
    """)
    customers = cursor.fetchall()
    
    # Get cards for selected customer
    customer_id = request.args.get('customer_id')
    cards = []
    if customer_id:
        cursor.execute("""
            SELECT id, CONCAT('****', RIGHT(AES_DECRYPT(card_number, %s), 4), ' - ', card_type) as card_info
            FROM CardDetails 
            WHERE userid = %s AND is_active = TRUE
        """, (AES_KEY, customer_id))
        cards = cursor.fetchall()
    
    conn.close()
    return render_template('create_invoice.html', customers=customers, cards=cards)

# ==================== REPORTS & AUDIT ====================
@app.route('/reports')
@login_required
@role_required('admin', 'merchant', 'auditor')
def reports():
    """View database reports using views"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    role = session['role']
    reports = {}
    
    try:
        if role == 'admin':
            cursor.execute("SELECT * FROM UserRoleSummary")
            reports['user_summary'] = cursor.fetchall()
            
            cursor.execute("SELECT * FROM CardStatistics")
            reports['card_stats'] = cursor.fetchall()
            
            cursor.execute("SELECT * FROM InvoiceSummary")
            reports['invoice_summary'] = cursor.fetchall()
            
        elif role == 'merchant':
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_invoices,
                    COALESCE(SUM(amount), 0) as total_revenue,
                    COALESCE(AVG(amount), 0) as avg_invoice
                FROM Invoices WHERE merchant_id = %s
            """, (session['userid'],))
            reports['performance'] = cursor.fetchone()
    except Exception as e:
        flash(f'Error loading reports: {str(e)}', 'danger')
    
    conn.close()
    log_access('VIEW_REPORTS')
    return render_template('reports.html', reports=reports, role=role)

@app.route('/audit-logs')
@login_required
@role_required('admin', 'auditor')
def audit_logs():
    """View security audit logs"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM SecurityAuditTrail ORDER BY timestamp DESC LIMIT 100")
        logs = cursor.fetchall()
    except:
        cursor.execute("""
            SELECT al.*, u.role
            FROM AccessLogs al
            LEFT JOIN Users u ON al.userid = u.userid
            ORDER BY al.timestamp DESC LIMIT 100
        """)
        logs = cursor.fetchall()
    
    conn.close()
    log_access('VIEW_AUDIT_LOGS')
    return render_template('audit_logs.html', logs=logs)

# ==================== PROFILE ====================
from flask import current_app # Import this at the top of your app.py if not already done

# ...

@app.route('/profile')
@login_required
def profile():
    """User profile"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Users WHERE userid = %s", (session['userid'],))
    user = cursor.fetchone()
    
    stats = {}
    if session['role'] == 'customer':
        cursor.execute("""
            SELECT COUNT(*) as total_cards
            FROM CardDetails WHERE userid = %s AND is_active = TRUE
        """, (session['userid'],))
        stats = cursor.fetchone()
    
    conn.close()
    
    # --- START OF FIX ---
    # 1. Access the application instance's config using current_app
    # 2. Get the timedelta object and convert it to total seconds, then minutes.
    try:
        session_lifetime_minutes = int(current_app.config['PERMANENT_SESSION_LIFETIME'].total_seconds() / 60)
    except AttributeError:
        # Fallback if PERMANENT_SESSION_LIFETIME is not properly configured as a timedelta
        session_lifetime_minutes = 30 # Default to 30 minutes, or a value that makes sense
    
    log_access('VIEW_PROFILE')
    
    # 3. Pass the calculated value to the template
    return render_template('profile.html', 
                           user=user, 
                           stats=stats,
                           session_lifetime=session_lifetime_minutes)
    # --- END OF FIX ---

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password"""
    if request.method == 'POST':
        current = request.form.get('current_password')
        new = request.form.get('new_password')
        confirm = request.form.get('confirm_password')
        
        if not all([current, new, confirm]):
            flash('All fields required.', 'danger')
            return render_template('change_password.html')
        
        if new != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('change_password.html')
        
        if len(new) < 8:
            flash('Password must be 8+ characters.', 'danger')
            return render_template('change_password.html')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Verify current password
            cursor.execute("""
                SELECT 1 FROM Users 
                WHERE userid = %s AND password_hash = SHA2(%s, 256)
            """, (session['userid'], current))
            
            if not cursor.fetchone():
                flash('Current password incorrect.', 'danger')
                conn.close()
                return render_template('change_password.html')
            
            # Update password
            cursor.execute("""
                UPDATE Users 
                SET password_hash = SHA2(%s, 256) 
                WHERE userid = %s
            """, (new, session['userid']))
            
            conn.commit()
            conn.close()
            
            log_access('CHANGE_PASSWORD')
            flash('Password changed successfully.', 'success')
            return redirect(url_for('profile'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('change_password.html')

# ==================== API ====================
@app.route('/test')
def test():
    """Simple test endpoint"""
    return "<h1>Server is Working!</h1><p>If you see this, Flask is running correctly.</p>"

@app.route('/health')
def health():
    """Health check"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'version': version,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# ==================== KERBEROS STATUS ====================
@app.route('/kerberos-status')
@login_required
def kerberos_status():
    """Display Kerberos ticket information"""
    ticket_info = get_ticket_info()
    
    if ticket_info:
        log_access('VIEW_KERBEROS_STATUS')
        return render_template('kerberos_status.html', ticket=ticket_info, has_ticket=True)
    else:
        return render_template('kerberos_status.html', has_ticket=False)

@app.route('/renew-ticket', methods=['POST'])
@login_required
def renew_ticket():
    """Manually renew Kerberos ticket"""
    ticket = session.get('kerberos_ticket')
    
    if not ticket:
        flash('No active ticket to renew.', 'danger')
        return redirect(url_for('kerberos_status'))
    
    client_ip = request.remote_addr
    new_ticket, message = KerberosTicket.renew_ticket(ticket, client_ip)
    
    if new_ticket:
        session['kerberos_ticket'] = new_ticket
        KerberosLogger.log_event('TICKET_RENEWED', session['userid'], message, db_config)
        flash('Kerberos ticket renewed successfully!', 'success')
    else:
        flash(f'Ticket renewal failed: {message}', 'danger')
    
    return redirect(url_for('kerberos_status'))

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    print("=" * 70)
    print("CREDIT CARD VAULT APPLICATION")
    print("=" * 70)
    
    # Check database
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Users")
        user_count = cursor.fetchone()[0]
        
        print(f"✓ Database: {db_name}")
        print(f"✓ Users: {user_count}")
        print(f"✓ AES Encryption: Enabled")
        print(f"✓ SHA-256 Hashing: Enabled")
        conn.close()
    except Exception as e:
        print(f"⚠ Database Error: {e}")
        print(f"⚠ Will try to create database and tables...")
    
    # SSL Configuration - OPTIONAL
    # Set to True for HTTPS (requires accepting browser warning)
    # Set to False for HTTP (easier for development, no warnings)
    
    USE_SSL = False  # Change to True to enable HTTPS with SSL
    
    cert_file = "localhost.pem"
    key_file = "localhost-key.pem"
    ssl_context = None
    
    if USE_SSL and os.path.exists(cert_file) and os.path.exists(key_file):
        ssl_context = (cert_file, key_file)
        print(f"✓ SSL Certificate: {cert_file}")
        print(f"✓ SSL Key: {key_file}")
        print("=" * 70)
        print("🔒 HTTPS Server running at: https://localhost:5000")
        print("⚠  Accept browser security warning for self-signed certificate")
    else:
        if not USE_SSL:
            print("ℹ  Running in HTTP mode for development")
        else:
            print("⚠  SSL certificates not found - running in HTTP mode")
        print("=" * 70)
        print("🌐 HTTP Server running at: http://localhost:5000")
        print("✓  Open your browser to: http://localhost:5000")
    
    print("=" * 70)
    
    # Run with optional SSL
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=ssl_context,
        debug=True
    )