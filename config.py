import os
from datetime import timedelta


class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'your-secret-key-change-in-production'

    # MongoDB Configuration
    MONGO_URI = os.environ.get(
        'MONGO_URI') or 'mongodb://localhost:27017/hyperlocal_community'

    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True

    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

    # Email Configuration (for future use)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in [
        'true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Pagination
    NOTICES_PER_PAGE = 10
    REQUESTS_PER_PAGE = 10
    MESSAGES_PER_PAGE = 50

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour

    # Application Settings
    APP_NAME = 'Hyperlocal Community Platform'
    APP_VERSION = '1.0.0'
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

    # Development specific settings
    MONGO_URI = os.environ.get(
        'MONGO_URI') or 'mongodb://localhost:27017/hyperlocal_community_dev'

    # Enable debug toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

    # In production, use environment variables for sensitive data
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MONGO_URI = os.environ.get('MONGO_URI')

    # Security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block'
    }


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

    # Use in-memory database for testing
    MONGO_URI = 'mongodb://localhost:27017/hyperlocal_community_test'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Environment variables


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])


# Database settings
DATABASE_SETTINGS = {
    'max_pool_size': 10,
    'min_pool_size': 1,
    'max_idle_time_ms': 30000,
    'server_selection_timeout_ms': 5000,
    'connect_timeout_ms': 20000,
    'socket_timeout_ms': 20000,
}

# Application constants
PRIORITY_LEVELS = {
    'urgent': {'label': 'Urgent', 'color': 'danger', 'icon': '🚨'},
    'high': {'label': 'High', 'color': 'warning', 'icon': '⚠️'},
    'medium': {'label': 'Medium', 'color': 'info', 'icon': 'ℹ️'},
    'low': {'label': 'Low', 'color': 'success', 'icon': '✅'}
}

STATUS_LEVELS = {
    'pending': {'label': 'Pending', 'color': 'warning', 'icon': '⏳'},
    'in_progress': {'label': 'In Progress', 'color': 'info', 'icon': '🔄'},
    'resolved': {'label': 'Resolved', 'color': 'success', 'icon': '✅'},
    'cancelled': {'label': 'Cancelled', 'color': 'danger', 'icon': '❌'}
}

CATEGORIES = {
    'plumbing': {'label': 'Plumbing', 'icon': '🚰'},
    'electrical': {'label': 'Electrical', 'icon': '⚡'},
    'carpentry': {'label': 'Carpentry', 'icon': '🔨'},
    'cleaning': {'label': 'Cleaning', 'icon': '🧹'},
    'security': {'label': 'Security', 'icon': '🔒'},
    'other': {'label': 'Other', 'icon': '📋'}
}

# Pagination settings
PAGINATION_SETTINGS = {
    'notices_per_page': 10,
    'requests_per_page': 10,
    'messages_per_page': 50,
    'users_per_page': 20
}

# File upload settings
UPLOAD_SETTINGS = {
    'max_file_size': 16 * 1024 * 1024,  # 16MB
    'allowed_extensions': {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'},
    'upload_folder': 'uploads',
    'max_files_per_request': 5
}

# Notification settings
NOTIFICATION_SETTINGS = {
    'email_notifications': True,
    'push_notifications': False,  # For future implementation
    'notification_retention_days': 30
}

# Chat settings
CHAT_SETTINGS = {
    'max_message_length': 1000,
    'message_retention_days': 90,
    'max_messages_per_user_per_minute': 10,
    'profanity_filter': True
}

# Security settings
SECURITY_SETTINGS = {
    'password_min_length': 6,
    'password_require_special_chars': False,
    'session_timeout_hours': 24,
    'max_login_attempts': 5,
    'lockout_duration_minutes': 15
}

# Default resident credentials
DEFAULT_RESIDENT_EMAIL = "resident@example.com"
DEFAULT_RESIDENT_PASSWORD = "Welcome@123"