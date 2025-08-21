"""
Security module for FRIDAY system.
Handles security-related functionality.
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from flask import session, request, current_app
from functools import wraps

class SecurityManager:
    """Handles security features for the application."""
    
    def __init__(self):
        self.failed_attempts = {}
        self.blocked_ips = {}
    
    def generate_csrf_token(self):
        """Generate CSRF token."""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_urlsafe(32)
        return session['csrf_token']
    
    def validate_csrf_token(self, token):
        """Validate CSRF token."""
        return session.get('csrf_token') == token
    
    def rate_limit_check(self, identifier, max_attempts=5, window_minutes=15):
        """Check if identifier is rate limited."""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Clean old attempts
        if identifier in self.failed_attempts:
            self.failed_attempts[identifier] = [
                attempt for attempt in self.failed_attempts[identifier]
                if attempt > window_start
            ]
        
        # Check if over limit
        attempts = self.failed_attempts.get(identifier, [])
        return len(attempts) < max_attempts
    
    def record_failed_attempt(self, identifier):
        """Record a failed attempt."""
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        self.failed_attempts[identifier].append(datetime.now())
    
    def is_safe_redirect(self, url):
        """Check if redirect URL is safe."""
        if not url:
            return False
        
        # Only allow relative URLs or same host
        if url.startswith('/'):
            return True
        
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        # No scheme or netloc means relative URL
        if not parsed.scheme and not parsed.netloc:
            return True
        
        return False
    
    def sanitize_filename(self, filename):
        """Sanitize filename for safe storage."""
        import re
        # Remove or replace dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading dots
        filename = filename.lstrip('.')
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext
        
        return filename or 'unnamed_file'
    
    def hash_password(self, password, salt=None):
        """Hash password with salt."""
        if salt is None:
            salt = secrets.token_hex(32)
        
        pwd_hash = hashlib.pbkdf2_hmac('sha256', 
                                     password.encode('utf-8'),
                                     salt.encode('utf-8'),
                                     100000)  # 100k iterations
        
        return salt + pwd_hash.hex()
    
    def verify_password(self, password, hashed):
        """Verify password against hash."""
        try:
            salt = hashed[:64]  # First 64 chars are salt
            stored_hash = hashed[64:]
            
            pwd_hash = hashlib.pbkdf2_hmac('sha256',
                                         password.encode('utf-8'),
                                         salt.encode('utf-8'),
                                         100000)
            
            return pwd_hash.hex() == stored_hash
        except:
            return False

# Global security manager
security_manager = SecurityManager()

def csrf_protect(f):
    """Decorator to protect against CSRF attacks."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.form.get('csrf_token')
            if not security_manager.validate_csrf_token(token):
                current_app.logger.warning(f"CSRF token validation failed for {request.endpoint}")
                return 'CSRF token validation failed', 403
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_attempts=5, window_minutes=15):
    """Decorator for rate limiting."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            identifier = request.remote_addr
            
            if not security_manager.rate_limit_check(identifier, max_attempts, window_minutes):
                current_app.logger.warning(f"Rate limit exceeded for {identifier} on {request.endpoint}")
                return 'Rate limit exceeded. Please try again later.', 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_security_event(event_type, details=None):
    """Log security events."""
    event = {
        'timestamp': datetime.now().isoformat(),
        'type': event_type,
        'ip': request.remote_addr if request else 'unknown',
        'user_agent': request.headers.get('User-Agent') if request else 'unknown',
        'details': details or {}
    }
    
    current_app.logger.warning(f"Security Event: {event}")

def get_client_ip():
    """Get client IP address, considering proxies."""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        return request.environ['HTTP_X_REAL_IP']
    else:
        return request.environ.get('REMOTE_ADDR', 'unknown')