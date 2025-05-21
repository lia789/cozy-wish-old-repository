"""
Development settings for CozyWish project.

These settings are optimized for development and debugging.
"""

from decouple import config, Csv
from .base import *
from utils.env import get_env, get_bool, get_list

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool('DEBUG', True)
ALLOWED_HOSTS = get_list('ALLOWED_HOSTS', ['localhost', '127.0.0.1', 'testserver'])

# Add debug toolbar in development
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = ["127.0.0.1"]

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Email configuration - use console backend for development
EMAIL_BACKEND = get_env('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = get_env('EMAIL_HOST', 'smtp.example.com')
EMAIL_PORT = get_env('EMAIL_PORT', 587, int)
EMAIL_HOST_USER = get_env('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = get_env('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = get_bool('EMAIL_USE_TLS', True)
DEFAULT_FROM_EMAIL = get_env('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# Session and cookie settings for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Development-specific logging
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['handlers']['console']['level'] = 'DEBUG'

# Add additional loggers for development
LOGGING['loggers'].update({
    'django.db.backends': {
        'handlers': ['console'],
        'level': 'DEBUG' if get_bool('LOG_SQL', False) else 'INFO',
        'propagate': False,
    },
})
