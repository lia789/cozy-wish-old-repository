#!/usr/bin/env python
"""
Test runner script for the notifications_app.
This script runs all tests for the notifications_app and generates a coverage report.

Usage:
    python run_tests.py [options]

Options:
    --verbose, -v: Run tests with verbose output
    --coverage, -c: Generate coverage report
    --html, -h: Generate HTML coverage report
    --specific=<test_file>, -s <test_file>: Run specific test file
    --help: Show this help message

Examples:
    python run_tests.py
    python run_tests.py --verbose
    python run_tests.py --coverage --html
    python run_tests.py --specific=test_models
"""

import os
import sys
import django
import argparse
from pathlib import Path

# Add the project root directory to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings')
django.setup()

from django.test.runner import DiscoverRunner
from django.conf import settings

def run_tests(verbosity=1, specific=None):
    """Run the tests"""
    test_runner = DiscoverRunner(verbosity=verbosity)
    
    if specific:
        # Run specific test file
        test_label = f'notifications_app.tests.{specific}'
        failures = test_runner.run_tests([test_label])
    else:
        # Run all tests
        failures = test_runner.run_tests(['notifications_app'])
    
    return failures

def run_coverage(html=False, specific=None):
    """Run tests with coverage"""
    try:
        import coverage
    except ImportError:
        print("Coverage package not installed. Install it with 'pip install coverage'")
        return 1
    
    cov = coverage.Coverage(source=['notifications_app'])
    cov.start()
    
    # Run the tests
    failures = run_tests(verbosity=1, specific=specific)
    
    cov.stop()
    cov.save()
    
    # Print coverage report
    print("\nCoverage Report:")
    cov.report()
    
    if html:
        # Generate HTML report
        cov.html_report(directory='htmlcov')
        print(f"\nHTML report generated in {os.path.join(os.getcwd(), 'htmlcov')}")
    
    return failures

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run tests for the notifications_app')
    parser.add_argument('--verbose', '-v', action='store_true', help='Run tests with verbose output')
    parser.add_argument('--coverage', '-c', action='store_true', help='Generate coverage report')
    parser.add_argument('--html', '-h', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('--specific', '-s', help='Run specific test file (without .py extension)')
    
    args = parser.parse_args()
    
    if args.coverage:
        # Run tests with coverage
        failures = run_coverage(html=args.html, specific=args.specific)
    else:
        # Run tests without coverage
        verbosity = 2 if args.verbose else 1
        failures = run_tests(verbosity=verbosity, specific=args.specific)
    
    sys.exit(failures)

if __name__ == '__main__':
    main()
