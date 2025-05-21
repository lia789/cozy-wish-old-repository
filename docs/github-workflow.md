# GitHub Workflow and Best Practices

This document outlines the GitHub workflow and best practices for the CozyWish project.

## Branching Strategy

We follow a Git Flow-inspired branching strategy with the following branches:

### Main Branches

- **main**: Production-ready code that is deployable to the production environment.
- **develop**: Integration branch where features are combined and tested before release.

### Supporting Branches

- **feature/***:  Feature branches for new functionality
- **bugfix/***:   Bugfix branches for fixing issues
- **release/***:  Release branches for preparing new production releases
- **hotfix/***:   Hotfix branches for urgent production fixes

## Branch Naming Conventions

- Feature branches: `feature/short-description` or `feature/issue-number-short-description`
- Bugfix branches: `bugfix/short-description` or `bugfix/issue-number-short-description`
- Release branches: `release/vX.Y.Z` (following semantic versioning)
- Hotfix branches: `hotfix/short-description` or `hotfix/issue-number-short-description`

## Workflow

### Feature Development

1. Create a new feature branch from `develop`:
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/my-feature
   ```

2. Develop your feature with regular commits:
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

3. Push your feature branch to GitHub:
   ```bash
   git push -u origin feature/my-feature
   ```

4. Create a pull request to merge your feature into `develop`.
5. After code review and approval, merge the pull request.

### Bug Fixing

1. Create a new bugfix branch from `develop`:
   ```bash
   git checkout develop
   git pull
   git checkout -b bugfix/issue-description
   ```

2. Fix the bug with clear commits:
   ```bash
   git add .
   git commit -m "Fix: Description of the bug fix"
   ```

3. Push your bugfix branch to GitHub:
   ```bash
   git push -u origin bugfix/issue-description
   ```

4. Create a pull request to merge your bugfix into `develop`.
5. After code review and approval, merge the pull request.

### Release Process

1. Create a release branch from `develop`:
   ```bash
   git checkout develop
   git pull
   git checkout -b release/v1.2.0
   ```

2. Make any final adjustments, version bumps, and documentation updates:
   ```bash
   git add .
   git commit -m "Bump version to 1.2.0"
   ```

3. Push the release branch to GitHub:
   ```bash
   git push -u origin release/v1.2.0
   ```

4. Create a pull request to merge the release into `main`.
5. After testing and approval, merge the pull request into `main`.
6. Create a pull request to merge the release back into `develop`.
7. Tag the release on `main`:
   ```bash
   git checkout main
   git pull
   git tag -a v1.2.0 -m "Release v1.2.0"
   git push origin v1.2.0
   ```

### Hotfix Process

1. Create a hotfix branch from `main`:
   ```bash
   git checkout main
   git pull
   git checkout -b hotfix/critical-issue
   ```

2. Fix the issue with clear commits:
   ```bash
   git add .
   git commit -m "Hotfix: Description of the critical fix"
   ```

3. Push the hotfix branch to GitHub:
   ```bash
   git push -u origin hotfix/critical-issue
   ```

4. Create a pull request to merge the hotfix into `main`.
5. After testing and approval, merge the pull request into `main`.
6. Create a pull request to merge the hotfix into `develop`.
7. Tag the hotfix on `main`:
   ```bash
   git checkout main
   git pull
   git tag -a v1.2.1 -m "Hotfix v1.2.1"
   git push origin v1.2.1
   ```

## Commit Message Guidelines

We follow the Conventional Commits specification for commit messages:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools

Example:
```
feat(venues): add search by location feature

Implement the ability to search venues by location using Google Maps API.
Closes #123
```

## Pull Request Guidelines

- Create focused, single-purpose pull requests
- Keep pull requests small and manageable
- Write clear descriptions using the PR template
- Link related issues
- Request reviews from appropriate team members
- Address all review comments
- Ensure all CI checks pass before merging

## Code Review Guidelines

- Be respectful and constructive
- Focus on the code, not the person
- Provide specific, actionable feedback
- Explain the reasoning behind your suggestions
- Approve only when all issues are addressed

## CI/CD Pipeline

Our CI/CD pipeline is configured using GitHub Actions:

1. **Continuous Integration (CI)**:
   - Runs on all pull requests to `develop` and `main`
   - Executes unit tests and integration tests
   - Performs code linting and style checks
   - Generates code coverage reports

2. **Continuous Deployment (CD)**:
   - **Staging Deployment**: Automatically deploys to staging when changes are pushed to `develop`
   - **Production Deployment**: Automatically deploys to production when changes are pushed to `main`

3. **Code Quality**:
   - Runs code quality checks on all pull requests
   - Performs security vulnerability scanning
   - Enforces code formatting standards
   - Integrates with SonarCloud for advanced code analysis
