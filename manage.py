#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Default to development settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings')

    # Use DJANGO_ENVIRONMENT to determine which settings module to use
    environment = os.environ.get('DJANGO_ENVIRONMENT')
    if environment:
        os.environ['DJANGO_SETTINGS_MODULE'] = f'project_root.settings'

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
