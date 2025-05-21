# Setting Up Branch Protection Rules in GitHub

This guide provides step-by-step instructions for setting up branch protection rules in GitHub to ensure code quality and prevent accidental changes to important branches.

## Why Use Branch Protection Rules?

Branch protection rules help you:

- Prevent direct pushes to important branches
- Require code reviews before merging
- Ensure CI checks pass before merging
- Maintain a clean and stable codebase

## Setting Up Branch Protection Rules

### 1. Navigate to Branch Protection Settings

1. Go to your GitHub repository
2. Click on the **Settings** tab
3. In the left sidebar, click on **Branches**
4. Under "Branch protection rules", click **Add rule**

### 2. Configure Branch Protection for Main Branch

1. In the "Branch name pattern" field, enter `main`
2. Check the following options:
   - **Require a pull request before merging**
     - Check "Require approvals" and set the number of required approvals (e.g., 1)
     - Optionally, check "Dismiss stale pull request approvals when new commits are pushed"
   - **Require status checks to pass before merging**
     - Check "Require branches to be up to date before merging"
     - In the search box, search for and select your required status checks (e.g., "test", "lint", "build")
   - **Require conversation resolution before merging**
   - **Do not allow bypassing the above settings**
3. Click **Create** or **Save changes**

### 3. Configure Branch Protection for Develop Branch

1. Click **Add rule** again
2. In the "Branch name pattern" field, enter `develop`
3. Configure similar settings as for the main branch
4. Click **Create** or **Save changes**

## Recommended Branch Protection Settings

### For Main Branch (Production)

- **Require pull request before merging**: Yes
  - Required approvals: 1-2
  - Dismiss stale approvals: Yes
- **Require status checks to pass**: Yes
  - Required checks: All CI/CD checks
- **Require conversation resolution**: Yes
- **Allow force pushes**: No
- **Allow deletions**: No
- **Restrict who can push**: Yes (optional)

### For Develop Branch (Staging)

- **Require pull request before merging**: Yes
  - Required approvals: 1
  - Dismiss stale approvals: Yes
- **Require status checks to pass**: Yes
  - Required checks: All CI checks
- **Require conversation resolution**: Yes
- **Allow force pushes**: No
- **Allow deletions**: No

## Best Practices

1. **Protect your default branch**: Always protect your default branch (usually `main`)
2. **Protect your deployment branches**: Protect any branch that is used for deployments (e.g., `develop`, `staging`)
3. **Require code reviews**: Code reviews help catch bugs and ensure code quality
4. **Require status checks**: Ensure all tests pass before merging
5. **Document your branch protection rules**: Make sure your team understands the rules

## Troubleshooting

### Common Issues

- **Cannot push to protected branch**: Create a pull request instead
- **Pull request cannot be merged**: Ensure all required checks pass and you have the required approvals
- **Status checks not appearing**: Ensure your CI/CD workflows are correctly configured

### Bypassing Branch Protection (Emergency Only)

In rare emergency situations, repository administrators can temporarily disable branch protection:

1. Go to repository settings
2. Navigate to Branches
3. Edit the branch protection rule
4. Uncheck "Do not allow bypassing the above settings"
5. Save changes
6. Make your emergency changes
7. Re-enable the setting immediately after
