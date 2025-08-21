"""
Configuration module for FRIDAY system.
Centralized configuration management.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    TEMPLATES_AUTO_RELOAD = True
    
    # Data directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__ + '/../'))
    DATA_DIR = os.getenv('DATA_DIR', os.path.join(BASE_DIR, 'state'))
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Authentication
    AUTH_ENABLED = os.getenv('AUTH_ENABLED', 'True').lower() == 'true'
    DEFAULT_USERNAME = os.getenv('FRIDAY_DEFAULT_USER', 'admin')
    DEFAULT_PASSWORD = os.getenv('FRIDAY_DEFAULT_PASS', 'friday123')
    
    # File upload limits
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '50')) * 1024 * 1024  # 50MB default
    
    # Render settings
    MAX_CONCURRENT_JOBS = int(os.getenv('MAX_CONCURRENT_JOBS', '3'))
    JOB_TIMEOUT_HOURS = int(os.getenv('JOB_TIMEOUT_HOURS', '2'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(DATA_DIR if DATA_DIR else '/tmp', 'logs', 'app.log')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test-secret-key'

def get_config():
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()