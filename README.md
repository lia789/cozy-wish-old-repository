# CozyWish

A Django-based platform for venue booking and management.

## Django Apps

The project consists of the following Django apps:

- **accounts_app**: Handles user authentication, profiles, and account management
  - Custom user model with email-based authentication
  - Customer and Service Provider profiles
  - Staff management for service providers
  - Authentication flows (login, signup, password reset)
  - Account deletion and security features

- utils
- review_app
- admin_app
- payments_app
- dashboard_app
- booking_cart_app
- discount_app
- venues_app
- notifications_app
- cms_app

## Make Commands

The project includes several useful make commands to simplify development and maintenance. You can view all available commands by running `make help`.

### Environment Setup

```bash
# Set up environment variables from .env.example
make setup-env

# Set up complete development environment (setup-env + full-reset-db + import dummy data)
make setup-dev-environment
```

### Running the Server

```bash
# Run development server with development settings
make run-dev

# Run development server with test settings
make run-test

# Run development server with staging settings
make run-staging

# Run development server with production settings
make run-prod
```

### Database Management

```bash
# Reset the database completely (drop DB, delete migrations, create new DB with superuser)
make full-reset-db

# Import dummy data for accounts_app
make accounts-app-db-import

# Import dummy data for venues_app
make venues-app-db-import

# Create database migrations
make makemigrations

# Apply database migrations
make migrate
```

### Development Tools

```bash
# Run tests
make test

# Run linting
make lint

# Run code formatting (black and isort)
make format

# Start Django shell (shell_plus with IPython)
make shell

# Collect static files
make collectstatic

# Create superuser
make superuser
```

## Getting Started

1. Clone the repository
2. Set up your virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and configure your environment variables
5. Set up the development environment: `make setup-dev-environment`
6. Run the development server: `python manage.py runserver`

## Project Structure

The project follows a modular structure with separate Django apps for different functionalities:

```
cozywish/
├── project_root/           # Project configuration
│   ├── settings/           # Split settings configuration
│   │   ├── __init__.py     # Settings loader
│   │   ├── base.py         # Base settings
│   │   ├── dev.py          # Development settings
│   │   ├── test.py         # Test settings
│   │   ├── staging.py      # Staging settings
│   │   └── prod.py         # Production settings
│   ├── urls.py             # Main URL configuration
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── accounts_app/           # User authentication and profiles
├── venues_app/             # Venue and service management
├── booking_cart_app/       # Booking and cart functionality
├── payments_app/           # Payment processing
├── dashboard_app/          # User dashboards
├── review_app/             # Review system
├── discount_app/           # Discount management
├── cms_app/                # Content management
├── notifications_app/      # Notification system
├── admin_app/              # Extended admin functionality
├── utils/                  # Utility functions and services
├── templates/              # HTML templates
├── static/                 # Static files
├── media/                  # User-uploaded files
├── requirements/           # Split requirements files
├── manage.py               # Django management script
└── .env                    # Environment variables
```

## Settings Configuration

The project uses a split settings approach for better organization and environment-specific configuration:

- **base.py**: Common settings shared across all environments
- **dev.py**: Development-specific settings (debugging, local database)
- **test.py**: Test-specific settings (in-memory database, faster password hashing)
- **staging.py**: Staging-specific settings (similar to production but with more debugging)
- **prod.py**: Production-specific settings (optimized for security and performance)

### Environment Variables

The project uses environment variables for configuration. You can set the environment by setting the `DJANGO_ENVIRONMENT` variable:

```bash
# For development (default)
export DJANGO_ENVIRONMENT=development

# For testing
export DJANGO_ENVIRONMENT=testing

# For staging
export DJANGO_ENVIRONMENT=staging

# For production
export DJANGO_ENVIRONMENT=production
```

See `.env.example` for all available configuration options.

## Git Branching Strategy

We follow a structured branching strategy to maintain code quality and streamline development:

### Main Branches

- **main**: Production-ready code. All code in this branch is deployable to production.
- **develop**: Integration branch for features. This is where features are combined and tested before release.

### Supporting Branches

- **feature/***:  Feature branches for new functionality (e.g., `feature/venue-search`)
- **bugfix/***:   Bugfix branches for fixing issues (e.g., `bugfix/login-error`)
- **release/***:  Release branches for preparing new production releases (e.g., `release/v1.2.0`)
- **hotfix/***:   Hotfix branches for urgent production fixes (e.g., `hotfix/payment-issue`)

### Branch Flow

1. Create feature branches from `develop`
2. When a feature is complete, create a pull request to merge back into `develop`
3. When ready to release, create a release branch from `develop`
4. After testing the release branch, merge it into both `main` and `develop`
5. If issues are found in production, create a hotfix branch from `main`
6. After fixing, merge the hotfix into both `main` and `develop`

## GitHub Workflows

The repository is configured with GitHub Actions for automated CI/CD:

### Continuous Integration (CI)

- Runs on all pull requests to `develop` and `main`
- Executes unit tests and integration tests
- Performs code linting and style checks
- Generates code coverage reports

### Continuous Deployment (CD)

- **Staging Deployment**: Automatically deploys to staging when changes are pushed to `develop`
- **Production Deployment**: Automatically deploys to production when changes are pushed to `main`

### Code Quality

- Runs code quality checks on all pull requests
- Performs security vulnerability scanning
- Enforces code formatting standards
- Integrates with SonarCloud for advanced code analysis

## Branch Protection Rules

The repository has branch protection rules to maintain code quality:

- **main** and **develop** branches are protected
- Direct pushes to protected branches are not allowed
- Pull requests require at least one review before merging
- CI checks must pass before merging is allowed
- Linear history is enforced (no merge commits)
