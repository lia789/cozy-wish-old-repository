import os
from pathlib import Path
from decouple import config, Csv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver', cast=Csv())




# Application definition

# Django apps
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.sites",
]

# Site ID for django.contrib.sites
SITE_ID = 1

# Third-party apps
THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "widget_tweaks",
    # "django_cron",  # Commented out due to compatibility issues with Django 5.0
]

# Local apps
LOCAL_APPS = [
    "accounts_app",
    "venues_app",
    "booking_cart_app",
    "payments_app",
    "dashboard_app",
    "cms_app",
    "review_app",
    "admin_app",
    "discount_app",
    "notifications_app",
    "utils",  # Utility app for image handling
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Add debug toolbar if in debug mode
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]

# Crispy forms settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"



# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "discount_app.middleware.DiscountMiddleware",
    "booking_cart_app.middleware.CartCleanupMiddleware",
]



# Add debug toolbar middleware if in debug mode
if DEBUG:
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]


ROOT_URLCONF = "project_root.urls"



# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'], # Add this line
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "booking_cart_app.context_processors.cart_context",
                "admin_app.context_processors.admin_context",
                "notifications_app.context_processors.notifications_context",
                "cms_app.context_processors.cms_context",
            ],
        },
    },
]

WSGI_APPLICATION = "project_root.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# SQLite configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# PostgreSQL configuration (commented out)
# DATABASES = {
#     'default': {
#         'ENGINE': config('DB_ENGINE'),
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST'),
#         'PORT': config('DB_PORT'),
#     }
# }



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

# Simplified password validators for service providers (only minimum length of 8)
SERVICE_PROVIDER_PASSWORD_VALIDATORS = [
    {
        "NAME": "accounts_app.validators.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        }
    },
]

# Simplified password validators for customers (only minimum length of 8)
CUSTOMER_PASSWORD_VALIDATORS = [
    {
        "NAME": "accounts_app.validators.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        }
    },
]

# Default to service provider validators
AUTH_PASSWORD_VALIDATORS = SERVICE_PROVIDER_PASSWORD_VALIDATORS




# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True



# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]


# Media files (User uploaded files)
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication settings
# Configure your authentication settings here
AUTH_USER_MODEL = 'accounts_app.CustomUser'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'accounts_app.backends.CustomModelBackend',
]

# Login/logout URLs
LOGIN_URL = 'accounts_app:login'
LOGOUT_URL = 'accounts_app:logout'
LOGIN_REDIRECT_URL = 'accounts_app:profile'

# Password reset timeout (in seconds)
PASSWORD_RESET_TIMEOUT = 86400  # 24 hours

# Session settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Default behavior when "Remember me" is checked
SESSION_COOKIE_SECURE = False  # Set to True in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'


# Email configuration
# Using console backend for development as specified in requirements
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.example.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@example.com')


# Django Cron settings (commented out due to compatibility issues with Django 5.0)
# CRON_CLASSES = [
#     'booking_cart_app.cron.CleanExpiredCartItemsCronJob',
# ]

# Logging configuration
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
