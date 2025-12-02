#!/usr/bin/env python3
"""
SSL Certificate Generator for Credit Card Vault
Generates self-signed SSL certificates for HTTPS
"""

from datetime import datetime, timedelta
import subprocess
import os
import sys

def generate_ssl_certificate():
    """Generate self-signed SSL certificate using OpenSSL"""
    
    print("=" * 70)
    print("SSL CERTIFICATE GENERATOR")
    print("=" * 70)
    print()
    
    # Certificate details
    cert_file = "localhost.pem"
    key_file = "localhost-key.pem"
    
    # Check if certificates already exist
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"⚠ Certificates already exist:")
        print(f"  - {cert_file}")
        print(f"  - {key_file}")
        response = input("\nOverwrite existing certificates? (y/n): ").lower()
        if response != 'y':
            print("✗ Certificate generation cancelled.")
            return False
        
        # Remove old certificates
        os.remove(cert_file)
        os.remove(key_file)
        print("✓ Old certificates removed")
    
    print("\nGenerating self-signed SSL certificate...")
    print()
    
    # Try using OpenSSL command
    try:
        # OpenSSL command to generate self-signed certificate
        openssl_cmd = [
            'openssl', 'req', '-x509',
            '-newkey', 'rsa:4096',
            '-keyout', key_file,
            '-out', cert_file,
            '-days', '365',
            '-nodes',
            '-subj', '/C=US/ST=State/L=City/O=CardVault/OU=IT/CN=localhost'
        ]
        
        subprocess.run(openssl_cmd, check=True, capture_output=True)
        
        print("✓ SSL certificate generated successfully!")
        print()
        print(f"✓ Certificate: {cert_file}")
        print(f"✓ Private Key: {key_file}")
        print(f"✓ Valid for: 365 days")
        print(f"✓ Common Name: localhost")
        print()
        print("=" * 70)
        print("HTTPS SERVER READY")
        print("=" * 70)
        print()
        print("Your server will now run with HTTPS enabled!")
        print("Access at: https://localhost:5000")
        print()
        print("⚠ Browser Security Warning:")
        print("  You'll see a warning because this is a self-signed certificate.")
        print("  This is NORMAL and SAFE for development.")
        print()
        print("To bypass the warning:")
        print("  1. Click 'Advanced'")
        print("  2. Click 'Proceed to localhost (unsafe)' or similar")
        print("  3. Accept the risk")
        print()
        return True
        
    except FileNotFoundError:
        print("✗ OpenSSL not found!")
        print()
        print("Installing OpenSSL...")
        print()
        print("Option 1 - Windows (Chocolatey):")
        print("  choco install openssl")
        print()
        print("Option 2 - Windows (Direct Download):")
        print("  Download from: https://slproweb.com/products/Win32OpenSSL.html")
        print()
        print("Option 3 - Use Python alternative below...")
        print()
        
        # Try Python alternative
        return generate_with_python()
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error generating certificate: {e}")
        print()
        print("Trying Python alternative...")
        return generate_with_python()

def generate_with_python():
    """Generate certificate using Python cryptography library"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend
        
        print("Using Python cryptography library...")
        print()
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"State"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"City"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"CardVault"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u"IT Department"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"localhost"),
                x509.DNSName(u"127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        # Write private key
        with open("localhost-key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Write certificate
        with open("localhost.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print("✓ SSL certificate generated successfully (Python method)!")
        print()
        print("✓ Certificate: localhost.pem")
        print("✓ Private Key: localhost-key.pem")
        print("✓ Valid for: 365 days")
        print("✓ Common Name: localhost")
        print()
        return True
        
    except ImportError:
        print("✗ Python cryptography library not installed!")
        print()
        print("Install with:")
        print("  pip install cryptography")
        print()
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    success = generate_ssl_certificate()
    
    if success:
        print("=" * 70)
        print("✅ SSL SETUP COMPLETE!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Restart your Flask server")
        print("  2. Access https://localhost:5000")
        print("  3. Accept browser security warning")
        print("  4. Enjoy secure HTTPS connection!")
        print()
        sys.exit(0)
    else:
        print("=" * 70)
        print("✗ SSL SETUP FAILED")
        print("=" * 70)
        print()
        print("The server will run in HTTP mode (less secure).")
        print("For production, please install OpenSSL and regenerate certificates.")
        print()
        sys.exit(1)

