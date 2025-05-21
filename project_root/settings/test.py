"""
Test settings for CozyWish project.

These settings are optimized for testing.
"""

from .base import *

# Set debug to False for testing
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Use in-memory SQLite database for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Use a faster password hasher for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations for testing
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Email configuration for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'CRITICAL',
        },
    },
}

# Disable debug toolbar for testing
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')
    MIDDLEWARE = [m for m in MIDDLEWARE if 'debug_toolbar' not in m]

# Use a test-specific cache backend
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable CSRF protection in tests for simplicity
MIDDLEWARE = [m for m in MIDDLEWARE if 'CsrfViewMiddleware' not in m]
