# Setting Up GitHub Branch Protection Rules

This guide provides detailed instructions for setting up branch protection rules in GitHub to ensure code quality and prevent accidental changes to important branches.

## Why Use Branch Protection Rules?

Branch protection rules help you:

1. Prevent direct pushes to important branches (like `main` and `develop`)
2. Require pull requests before merging changes
3. Require status checks to pass before merging
4. Require code reviews before merging
5. Prevent force pushes that could rewrite history

## Setting Up Branch Protection Rules

### Steps to Configure Branch Protection

1. Go to your GitHub repository
2. Click on the **Settings** tab
3. In the left sidebar, click on **Branches**
4. Under "Branch protection rules", click **Add rule**
5. In the "Branch name pattern" field, enter the branch name you want to protect (e.g., `main` or `develop`)
6. Configure the protection settings (see below)
7. Click **Create** or **Save changes**

### Recommended Protection Settings

#### For `main` Branch (Production)

- ✅ **Require a pull request before merging**
  - ✅ Require approvals (at least 1)
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners (if you have a CODEOWNERS file)

- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - ✅ Select status checks that must pass:
    - CI workflow (tests)
    - Code quality checks
    - Any other checks you have configured

- ✅ **Require conversation resolution before merging**

- ✅ **Do not allow bypassing the above settings**

- ✅ **Restrict who can push to matching branches** (optional, for stricter control)
  - Add administrators or specific teams who can push directly

#### For `develop` Branch (Staging)

Similar to `main`, but you might want to be slightly less restrictive:

- ✅ **Require a pull request before merging**
  - ✅ Require approvals (at least 1)

- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - ✅ Select status checks that must pass:
    - CI workflow (tests)
    - Code quality checks

- ✅ **Require conversation resolution before merging**

## Branch Protection for GitHub Actions

To ensure your GitHub Actions workflows work correctly with branch protection:

1. Make sure your workflow files are committed to the protected branches
2. Configure your workflows to run on pull requests to protected branches
3. Set up status checks in your workflows that report back to GitHub

Example workflow configuration:

```yaml
name: CI

on:
  push:
    branches: [ develop, main ]
  pull_request:
    branches: [ develop, main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      # Your test steps here
```

## Best Practices

1. **Always protect your `main` branch** - This should represent your production-ready code
2. **Consider protecting your `develop` branch** - This should represent your staging environment
3. **Use descriptive branch names** for feature branches (e.g., `feature/add-login-page`)
4. **Delete branches after merging** to keep your repository clean
5. **Document your branch strategy** in your README.md file
6. **Use semantic versioning** for releases
7. **Tag releases** on the `main` branch

## Troubleshooting

### Common Issues

1. **Cannot push to protected branch**
   - Solution: Create a pull request instead of pushing directly

2. **Pull request cannot be merged**
   - Check that all required status checks are passing
   - Ensure you have the required number of approvals
   - Make sure all conversations are resolved
   - Update the branch if it's out of date with the base branch

3. **Status checks not appearing**
   - Make sure your workflow files are correctly configured
   - Check the Actions tab for any workflow run errors

4. **Need to bypass protection in emergency**
   - Repository administrators can temporarily disable branch protection
   - Re-enable protection immediately after the emergency change
