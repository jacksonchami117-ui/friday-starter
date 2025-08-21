"""
Authentication module for FRIDAY system.
Provides simple session-based authentication without committing secrets.
"""

import os
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_default_credentials():
    """Get default credentials from environment or use defaults."""
    default_username = os.getenv('FRIDAY_DEFAULT_USER', 'admin')
    default_password = os.getenv('FRIDAY_DEFAULT_PASS', 'friday123')
    return default_username, default_password

def verify_credentials(username, password):
    """Verify login credentials against environment variables or defaults."""
    default_username, default_password = get_default_credentials()
    
    # Simple hash comparison to avoid storing plaintext
    provided_hash = hashlib.sha256(f"{username}:{password}".encode()).hexdigest()
    expected_hash = hashlib.sha256(f"{default_username}:{default_password}".encode()).hexdigest()
    
    return provided_hash == expected_hash

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login endpoint."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password.', 'error')
            return render_template('login.html')
        
        if verify_credentials(username, password):
            session['logged_in'] = True
            session['username'] = username
            flash('Successfully logged in!', 'success')
            
            # Redirect to the page they were trying to access, or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
            current_app.logger.warning(f"Failed login attempt for username: {username}")
    
    return render_template('login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logout endpoint."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/status')
def status():
    """Check authentication status."""
    if session.get('logged_in'):
        return {
            'authenticated': True,
            'username': session.get('username'),
            'message': 'User is logged in'
        }
    else:
        return {
            'authenticated': False,
            'message': 'User is not logged in'
        }, 401