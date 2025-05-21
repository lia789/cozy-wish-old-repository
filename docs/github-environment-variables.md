# Setting Up GitHub Environment Variables

This guide provides detailed instructions for setting up environment variables in GitHub for use with GitHub Actions workflows.

## Types of Environment Variables in GitHub

GitHub offers two main ways to store environment variables:

1. **Repository Secrets**: Available to all workflows in the repository
2. **Environment Secrets**: Available only to workflows that reference the specific environment

## Setting Up Repository Secrets

Repository secrets are available to all workflows in your repository. They're ideal for variables that are used across all environments or for variables that don't change between environments.

### Steps to Add Repository Secrets

1. Go to your GitHub repository
2. Click on the **Settings** tab
3. In the left sidebar, click on **Secrets and variables** > **Actions**
4. Click on **New repository secret**
5. Enter the name of the secret (e.g., `SECRET_KEY`, `DATABASE_URL`)
   - Use uppercase letters and underscores for secret names
   - Names are case-sensitive
6. Enter the value of the secret
7. Click **Add secret**

![Repository Secrets](https://docs.github.com/assets/cb-40465/mw-1440/images/help/repository/actions-secret-repository-create.webp)

## Setting Up Environment Secrets

Environment secrets are available only to workflows that reference the specific environment. They're ideal for environment-specific variables like database URLs, API keys, etc.

### Steps to Create an Environment

1. Go to your GitHub repository
2. Click on the **Settings** tab
3. In the left sidebar, click on **Environments**
4. Click on **New environment**
5. Enter a name for the environment (e.g., "production", "staging", "development")
6. Click **Configure environment**

### Steps to Add Environment Secrets

1. After creating or selecting an environment, scroll down to the **Environment secrets** section
2. Click **Add secret**
3. Enter the name of the secret (e.g., `PRODUCTION_DATABASE_URL`, `STAGING_API_KEY`)
4. Enter the value of the secret
5. Click **Add secret**

### Environment Protection Rules (Optional)

You can also set up protection rules for environments:

1. In the environment settings, scroll to the **Deployment protection rules** section
2. Enable **Required reviewers** to require specific people to approve workflow runs that use this environment
3. Enable **Wait timer** to set a waiting period before workflows can access the environment

## Using Secrets in GitHub Actions Workflows

To use secrets in your GitHub Actions workflows, reference them using the `secrets` context:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Specify the environment to use its secrets
    
    steps:
    - name: Deploy with environment variables
      env:
        SECRET_KEY: ${{ secrets.SECRET_KEY }}
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
      run: |
        # Your deployment commands here
        echo "Deploying with secrets..."
```

## Best Practices

1. **Use environment-specific secrets** for values that differ between environments
2. **Use repository secrets** for values that are the same across all environments
3. **Never print secrets** in workflow logs
4. **Rotate secrets** regularly for security
5. **Use descriptive names** for your secrets
6. **Document required secrets** in your repository's README

## Common Environment Variables for Django Projects

For Django projects, consider setting up the following environment variables:

- `SECRET_KEY`: Django's secret key
- `DEBUG`: Set to 'False' for production environments
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Database connection string
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Email settings
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: For S3 storage
- `SENTRY_DSN`: For error tracking with Sentry
