"""
Kerberos-Inspired Authentication Module for Credit Card Vault
Implements ticket-based authentication inspired by Kerberos protocol
"""

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, flash, redirect, url_for
import mysql.connector

# Kerberos-like configuration
TICKET_LIFETIME = 1800  # 30 minutes (like TGT lifetime)
SERVICE_KEY = "vault-service-key-2024"  # Service principal key
REALM = "CARDVAULT.LOCAL"  # Kerberos realm


class KerberosTicket:
    """Represents a Kerberos-style authentication ticket"""
    
    @staticmethod
    def generate_ticket(userid, role, client_ip):
        """
        Generate a Kerberos-style Ticket Granting Ticket (TGT)
        
        Ticket Structure:
        - Principal: userid@REALM
        - Session Key: Random cryptographic key
        - Timestamp: Issue time
        - Lifetime: Valid duration
        - Client Address: IP address
        - Service: Target service name
        """
        timestamp = int(time.time())
        expiry = timestamp + TICKET_LIFETIME
        
        # Generate session key (like Kerberos session key)
        session_key = secrets.token_hex(32)
        
        # Create ticket payload
        ticket_data = f"{userid}@{REALM}|{role}|{timestamp}|{expiry}|{client_ip}|{session_key}"
        
        # Sign ticket with service key (like Kerberos ticket encryption)
        signature = hashlib.sha256(
            f"{ticket_data}{SERVICE_KEY}".encode()
        ).hexdigest()
        
        ticket = {
            'principal': f"{userid}@{REALM}",
            'userid': userid,
            'role': role,
            'session_key': session_key,
            'issued_at': timestamp,
            'expires_at': expiry,
            'client_address': client_ip,
            'signature': signature,
            'realm': REALM,
            'service': 'vault-service'
        }
        
        return ticket
    
    @staticmethod
    def validate_ticket(ticket, client_ip):
        """
        Validate a Kerberos-style ticket
        
        Checks:
        1. Ticket signature (authenticity)
        2. Expiration time (still valid)
        3. Client IP address (prevents ticket theft)
        4. Realm validity
        """
        if not ticket:
            return False, "No ticket provided"
        
        # Check expiration
        current_time = int(time.time())
        if current_time > ticket.get('expires_at', 0):
            return False, "Ticket expired (TGT lifetime exceeded)"
        
        # Verify client IP (prevents ticket replay attacks)
        if ticket.get('client_address') != client_ip:
            return False, "Client address mismatch (possible ticket theft)"
        
        # Verify signature (ticket integrity)
        ticket_data = f"{ticket['userid']}@{REALM}|{ticket['role']}|{ticket['issued_at']}|{ticket['expires_at']}|{ticket['client_address']}|{ticket['session_key']}"
        expected_signature = hashlib.sha256(
            f"{ticket_data}{SERVICE_KEY}".encode()
        ).hexdigest()
        
        if ticket.get('signature') != expected_signature:
            return False, "Invalid ticket signature (tampering detected)"
        
        # Verify realm
        if ticket.get('realm') != REALM:
            return False, "Invalid realm"
        
        return True, "Ticket valid"
    
    @staticmethod
    def renew_ticket(old_ticket, client_ip):
        """
        Renew an existing ticket (like Kerberos ticket renewal)
        Similar to getting a new TGT with an existing valid TGT
        """
        valid, message = KerberosTicket.validate_ticket(old_ticket, client_ip)
        
        if not valid:
            return None, message
        
        # Issue new ticket with fresh timestamp
        return KerberosTicket.generate_ticket(
            old_ticket['userid'],
            old_ticket['role'],
            client_ip
        ), "Ticket renewed successfully"


class KerberosAuth:
    """Kerberos-style authentication handler"""
    
    @staticmethod
    def authenticate(userid, password, db_config):
        """
        Authenticate user and issue TGT (Ticket Granting Ticket)
        Similar to Kerberos AS (Authentication Service) exchange
        """
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Verify credentials with KDC (database)
            cursor.execute("""
                SELECT userid, role, full_name, is_active 
                FROM Users 
                WHERE userid = %s AND password_hash = SHA2(%s, 256)
            """, (userid, password))
            
            user = cursor.fetchone()
            conn.close()
            
            if not user or not user['is_active']:
                return None, "Authentication failed: Invalid credentials"
            
            # Issue TGT (Ticket Granting Ticket)
            client_ip = request.remote_addr
            ticket = KerberosTicket.generate_ticket(
                user['userid'],
                user['role'],
                client_ip
            )
            
            return ticket, "Authentication successful - TGT issued"
            
        except Exception as e:
            return None, f"Authentication error: {str(e)}"
    
    @staticmethod
    def get_service_ticket(tgt, service_name):
        """
        Exchange TGT for Service Ticket (ST)
        Similar to Kerberos TGS (Ticket Granting Service) exchange
        """
        client_ip = request.remote_addr
        valid, message = KerberosTicket.validate_ticket(tgt, client_ip)
        
        if not valid:
            return None, message
        
        # Generate service-specific ticket
        service_ticket = {
            'principal': tgt['principal'],
            'userid': tgt['userid'],
            'role': tgt['role'],
            'service': service_name,
            'session_key': secrets.token_hex(32),
            'issued_at': int(time.time()),
            'expires_at': int(time.time()) + 600,  # 10 min for service tickets
            'client_address': client_ip,
            'from_tgt': tgt['signature'][:16]  # Reference to parent TGT
        }
        
        return service_ticket, "Service ticket granted"


def kerberos_required(f):
    """
    Decorator for Kerberos ticket-based authentication
    Similar to @login_required but uses Kerberos tickets
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if ticket exists in session
        ticket = session.get('kerberos_ticket')
        
        if not ticket:
            flash('Authentication required. Please login with Kerberos.', 'warning')
            return redirect(url_for('login'))
        
        # Validate ticket
        client_ip = request.remote_addr
        valid, message = KerberosTicket.validate_ticket(ticket, client_ip)
        
        if not valid:
            session.clear()
            flash(f'Ticket validation failed: {message}', 'danger')
            return redirect(url_for('login'))
        
        # Check if ticket needs renewal (< 5 minutes remaining)
        time_remaining = ticket['expires_at'] - int(time.time())
        if time_remaining < 300:  # Less than 5 minutes
            new_ticket, msg = KerberosTicket.renew_ticket(ticket, client_ip)
            if new_ticket:
                session['kerberos_ticket'] = new_ticket
                session['ticket_renewed'] = datetime.now().isoformat()
        
        return f(*args, **kwargs)
    
    return decorated_function


def kerberos_role_required(*roles):
    """
    Decorator for role-based access with Kerberos tickets
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ticket = session.get('kerberos_ticket')
            
            if not ticket:
                flash('Authentication required.', 'warning')
                return redirect(url_for('login'))
            
            # Validate ticket
            client_ip = request.remote_addr
            valid, message = KerberosTicket.validate_ticket(ticket, client_ip)
            
            if not valid:
                session.clear()
                flash(f'Ticket validation failed: {message}', 'danger')
                return redirect(url_for('login'))
            
            # Check role
            if ticket.get('role') not in roles:
                flash('Access denied. Insufficient privileges.', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


class KerberosLogger:
    """Log Kerberos authentication events"""
    
    @staticmethod
    def log_event(event_type, userid, details, db_config):
        """Log Kerberos-related security events"""
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO AccessLogs (userid, action, table_name, record_id, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                userid,
                f"KERBEROS_{event_type}",
                'KerberosAuth',
                None,
                request.remote_addr,
                request.headers.get('User-Agent')
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Logging error: {e}")


# Ticket information helper
def get_ticket_info():
    """Get current ticket information for display"""
    ticket = session.get('kerberos_ticket')
    if not ticket:
        return None
    
    issued = datetime.fromtimestamp(ticket['issued_at'])
    expires = datetime.fromtimestamp(ticket['expires_at'])
    time_remaining = ticket['expires_at'] - int(time.time())
    
    return {
        'principal': ticket['principal'],
        'realm': ticket['realm'],
        'service': ticket['service'],
        'issued_at': issued.strftime('%Y-%m-%d %H:%M:%S'),
        'expires_at': expires.strftime('%Y-%m-%d %H:%M:%S'),
        'time_remaining_seconds': time_remaining,
        'time_remaining_minutes': time_remaining // 60,
        'session_key_preview': ticket['session_key'][:8] + '...',
        'renewable': time_remaining > 300
    }

