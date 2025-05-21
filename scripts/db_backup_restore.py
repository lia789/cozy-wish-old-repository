#!/usr/bin/env python
"""
Database backup and restore script for CozyWish project.

This script provides commands for backing up and restoring the PostgreSQL database.
It supports both development and production environments.

Usage:
    python db_backup_restore.py backup [--env=ENV]
    python db_backup_restore.py restore FILENAME [--env=ENV]
    python db_backup_restore.py list [--env=ENV]
    python db_backup_restore.py help

Options:
    --env=ENV     Environment to use (development, staging, production) [default: development]
"""

import os
import sys
import subprocess
import datetime
import glob
from pathlib import Path

# Add the project root directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings')

# Import Django and setup
import django
django.setup()

from django.conf import settings
from django.core.management import call_command


def get_backup_dir():
    """Get the backup directory and create it if it doesn't exist."""
    backup_dir = BASE_DIR / 'backups'
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def get_timestamp():
    """Get a timestamp string for the backup filename."""
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


def backup_database(env='development'):
    """Backup the database."""
    backup_dir = get_backup_dir()
    timestamp = get_timestamp()
    
    # Get database settings
    db_settings = settings.DATABASES['default']
    db_engine = db_settings['ENGINE']
    
    if 'postgresql' in db_engine:
        # PostgreSQL backup
        backup_file = backup_dir / f"backup_{env}_{timestamp}.dump"
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_host = db_settings.get('HOST', 'localhost')
        db_port = db_settings.get('PORT', '5432')
        
        cmd = [
            'pg_dump',
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-F', 'c',  # Custom format (compressed)
            '-b',  # Include large objects
            '-v',  # Verbose
            '-f', str(backup_file),
            db_name
        ]
        
        print(f"Backing up PostgreSQL database {db_name} to {backup_file}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Backup completed successfully: {backup_file}")
            return str(backup_file)
        else:
            print(f"Error backing up database: {result.stderr}")
            return None
    else:
        # SQLite or other database - use Django's dumpdata
        backup_file = backup_dir / f"backup_{env}_{timestamp}.json"
        print(f"Backing up database to {backup_file}...")
        
        with open(backup_file, 'w') as f:
            call_command('dumpdata', '--indent=2', '--exclude=contenttypes', '--exclude=auth.Permission', stdout=f)
        
        print(f"Backup completed successfully: {backup_file}")
        return str(backup_file)


def restore_database(filename, env='development'):
    """Restore the database from a backup file."""
    backup_file = Path(filename)
    
    if not backup_file.exists():
        print(f"Error: Backup file {backup_file} does not exist")
        return False
    
    # Get database settings
    db_settings = settings.DATABASES['default']
    db_engine = db_settings['ENGINE']
    
    if backup_file.suffix == '.dump' and 'postgresql' in db_engine:
        # PostgreSQL restore
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_host = db_settings.get('HOST', 'localhost')
        db_port = db_settings.get('PORT', '5432')
        
        cmd = [
            'pg_restore',
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-d', db_name,
            '-v',  # Verbose
            '--clean',  # Clean (drop) database objects before recreating
            '--if-exists',  # Use IF EXISTS when dropping objects
            '--no-owner',  # Do not set ownership of objects to match the original database
            str(backup_file)
        ]
        
        print(f"Restoring PostgreSQL database {db_name} from {backup_file}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Restore completed successfully")
            return True
        else:
            print(f"Error restoring database: {result.stderr}")
            return False
    elif backup_file.suffix == '.json':
        # JSON restore (Django loaddata)
        print(f"Restoring database from {backup_file}...")
        call_command('loaddata', str(backup_file))
        print(f"Restore completed successfully")
        return True
    else:
        print(f"Error: Unsupported backup file format: {backup_file.suffix}")
        return False


def list_backups(env=None):
    """List all available backups."""
    backup_dir = get_backup_dir()
    
    # Get all backup files
    dump_files = glob.glob(str(backup_dir / "backup_*.dump"))
    json_files = glob.glob(str(backup_dir / "backup_*.json"))
    backup_files = dump_files + json_files
    
    if not backup_files:
        print("No backup files found")
        return
    
    # Filter by environment if specified
    if env:
        backup_files = [f for f in backup_files if f"_{env}_" in f]
    
    # Sort by modification time (newest first)
    backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    print(f"Available backup files ({len(backup_files)}):")
    for i, backup_file in enumerate(backup_files, 1):
        file_path = Path(backup_file)
        file_size = file_path.stat().st_size / (1024 * 1024)  # Size in MB
        mod_time = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
        print(f"{i}. {file_path.name} ({file_size:.2f} MB, {mod_time})")


def print_help():
    """Print help message."""
    print(__doc__)


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    # Parse environment option
    env = 'development'
    for arg in sys.argv[2:]:
        if arg.startswith('--env='):
            env = arg.split('=')[1]
    
    if command == 'backup':
        backup_database(env)
    elif command == 'restore':
        if len(sys.argv) < 3 or sys.argv[2].startswith('--'):
            print("Error: Missing backup file name")
            print_help()
            return
        restore_database(sys.argv[2], env)
    elif command == 'list':
        list_backups(env)
    elif command in ('help', '--help', '-h'):
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == '__main__':
    main()
