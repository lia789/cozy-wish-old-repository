"""
Django settings for CozyWish project.

This settings module uses a split settings approach where:
- base.py contains common settings
- dev.py contains development-specific settings
- test.py contains test-specific settings
- staging.py contains staging-specific settings
- prod.py contains production-specific settings

The environment variable DJANGO_SETTINGS_MODULE is used to determine which
settings module to use. If not set, it defaults to development settings.
"""

import os
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

# Find the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Default to development settings
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .prod import *
elif environment == 'staging':
    from .staging import *
elif environment == 'testing':
    from .test import *
else:
    from .dev import *
