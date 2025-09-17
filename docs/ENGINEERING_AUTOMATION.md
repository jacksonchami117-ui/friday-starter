# Engineering Automation Setup

This document provides an overview of the engineering automation and quality tooling that has been set up for the friday-starter repository.

## 🚀 Quick Start

After merging this PR, follow these steps to activate the automation:

### 1. Install GitHub Apps

Install these apps for your repository (one-click installs):

- [Renovate App](https://github.com/apps/renovate) - Automated dependency updates
- [Mergify App](https://github.com/apps/mergify) - Automated merge workflows
- [SonarCloud App](https://github.com/apps/sonarcloud) - Code quality analysis
- [Codecov App](https://github.com/apps/codecov) - Test coverage reporting
- [Trivy Security App](https://github.com/apps/trivy) - Security scanning
- [Snyk App](https://github.com/apps/snyk) - Dependency security (optional)
- [Settings App](https://github.com/apps/settings) - Repository settings as code

### 2. Configure Secrets

Add these secrets in your repository settings:

- `SONAR_TOKEN` - SonarCloud authentication token
- `SONAR_PROJECT_KEY` - Set to `jacksonchami117-ui_friday-starter`
- `CODECOV_TOKEN` - Codecov upload token (if private repo)
- `SNYK_TOKEN` - Snyk authentication token (optional)

### 3. Update Configuration

- Update contact information in `SECURITY.md`
- Review and adjust `sonar-project.properties` for your SonarCloud setup

## 📋 What's Included

### Dependency Management
- **Renovate** (`/.github/renovate.json`)
  - Automated dependency updates
  - Minor/patch updates auto-merged
  - Scheduled for weekends only
  - Groups related updates

### Merge Automation
- **Mergify** (`/.mergify.yml`)
  - Merge queue for controlled deployments
  - Auto-merge for approved PRs with passing CI
  - Special handling for dependency updates
  - Requires: build, coverage, sonar, trivy checks

### Release Management
- **Release Drafter** (`/.github/release-drafter.yml`, `/.github/workflows/release-drafter.yml`)
  - Automated release notes generation
  - Categorizes changes by labels
  - Semantic versioning support

### Code Quality
- **SonarCloud** (`/.github/workflows/sonarcloud.yml`, `/sonar-project.properties`)
  - Static code analysis
  - Security vulnerability detection
  - Code smell identification
  - Technical debt tracking

### Test Coverage
- **Codecov** (`/codecov.yml`, `/.github/workflows/coverage.yml`)
  - Coverage thresholds: 80% project, 70% patch
  - Informational status (won't block merges)
  - Coverage reporting and trends

### Security Scanning
- **Trivy** (`/.github/workflows/trivy.yml`)
  - Filesystem vulnerability scanning
  - Docker image security scanning
  - SARIF upload to GitHub Security tab
  - Weekly scheduled scans

- **Snyk** (`/.github/workflows/snyk.yml`) - Optional
  - Dependency vulnerability scanning
  - Only runs if `SNYK_TOKEN` is configured
  - Continuous monitoring mode

### Repository Hygiene
- **Auto-labeler** (`/.github/labeler.yml`, `/.github/workflows/labeler.yml`)
  - Automatic PR labeling based on file changes
  - Categories: documentation, tests, ci, dependencies, backend, frontend, config

- **Issue Templates** (`/.github/ISSUE_TEMPLATE/`)
  - Bug report template with structured fields
  - Feature request template with priority levels

- **PR Template** (`/.github/pull_request_template.md`)
  - Comprehensive checklist for contributors
  - Security, testing, and documentation reminders

- **Security Policy** (`/SECURITY.md`)
  - Vulnerability disclosure process
  - Security best practices
  - Contact information placeholders

### Repository Settings
- **Settings as Code** (`/.github/settings.yml`)
  - Branch protection rules
  - Required status checks
  - Repository configuration
  - Label management

## 🔧 Workflow Details

### CI/CD Pipeline

The automation includes several workflows that run on every PR:

1. **Build** (`/.github/workflows/ci.yml`) - Existing, updated with proper naming
2. **Coverage** (`/.github/workflows/coverage.yml`) - Test coverage analysis
3. **SonarCloud** (`/.github/workflows/sonarcloud.yml`) - Code quality analysis
4. **Trivy** (`/.github/workflows/trivy.yml`) - Security scanning
5. **Snyk** (`/.github/workflows/snyk.yml`) - Dependency security (optional)
6. **Auto Label** (`/.github/workflows/labeler.yml`) - Automatic PR labeling

### Merge Requirements

Through Mergify and Settings app, PRs require:
- ✅ Build passing
- ✅ Coverage analysis complete
- ✅ SonarCloud quality gate passed
- ✅ Trivy security scan clean
- ✅ At least 1 approving review
- ✅ Up-to-date with main branch

### Automated Actions

- **Dependency PRs**: Auto-approved and merged for patch/minor updates
- **Security PRs**: Fast-tracked through merge queue
- **Release Notes**: Updated automatically on merge to main
- **Labels**: Applied automatically based on changed files

## 🛡️ Security Features

- Vulnerability scanning with Trivy and Snyk
- Automated security updates via Renovate
- Security policy with disclosure process
- Required signed commits (via Settings app)
- Minimal workflow permissions
- Secret scanning alerts enabled

## 📊 Quality Metrics

The setup tracks:
- Test coverage (target: 80% project, 70% patch)
- Code quality metrics via SonarCloud
- Security vulnerabilities
- Dependency freshness
- PR review coverage

## 🔄 Maintenance

The automation is designed to be low-maintenance:
- Dependencies updated automatically
- Security issues flagged immediately
- Quality trends tracked over time
- Configuration as code in version control

## 📚 Resources

- [Renovate Documentation](https://docs.renovatebot.com/)
- [Mergify Documentation](https://docs.mergify.io/)
- [SonarCloud Documentation](https://docs.sonarcloud.io/)
- [Codecov Documentation](https://docs.codecov.io/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [GitHub Settings App](https://probot.github.io/apps/settings/)

## 🔍 Troubleshooting

Common issues and solutions:

### SonarCloud Setup
1. Create account at sonarcloud.io
2. Import your repository
3. Generate token and add to secrets
4. Update organization in `sonar-project.properties`

### Coverage Issues
- Ensure tests run and generate coverage.xml
- Check CODECOV_TOKEN is set (if private repo)
- Verify test paths in workflow

### Mergify Not Working
- Check required status checks match workflow job names
- Ensure Mergify app is installed
- Verify conditions in `.mergify.yml`

### Security Scans Failing
- Review SARIF output in Security tab
- Update exclusions if needed
- Check for false positives in scanner output