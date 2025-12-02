# GitHub Setup Guide

## Initial Repository Setup

### 1. Create Repository on GitHub
1. Go to https://github.com/new
2. Name: `max-pain-analysis-public`
3. Description: "Advanced Financial Market Scanner with AI-Powered Options Analysis"
4. Make it **PUBLIC** (for open-source)
5. Initialize with README: NO (we have our own)
6. Add .gitignore: NO (we have our own)
7. Add license: Choose MIT or BSD-2-Clause
8. Click "Create repository"

### 2. Initialize Local Repository
```bash
cd c:\Users\urbin\SCANNER\max-pain-analysis-public

# If git not initialized
git init

# Configure git
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add remote
git remote add origin https://github.com/yourusername/max-pain-analysis-public.git
```

### 3. Verify Files Before Commit

**DO NOT COMMIT:**
- `.env` (use `.env.example` instead)
- `__pycache__/` directories
- `.streamlit/` directory
- `*.pyc` files
- `auth_data/passwords.db` (user data)

**DO COMMIT:**
- `app.py`
- `requirements.txt`
- `.gitignore`
- `.env.example`
- `SECURITY.md`
- `AUDIT_REPORT.md`
- `API_DEPENDENCIES.md`
- `README.md`
- `DEPLOYMENT.md`
- `.github/workflows/`

### 4. First Commit

```bash
# Add all files (respects .gitignore)
git add .

# Verify what will be committed
git status

# Create commit
git commit -m "Initial commit: Pro Scanner financial analysis application

- Core application with Streamlit framework
- Options analysis with gamma exposure tracking
- Real-time market data integration
- FinViz Elite stock screener
- Secure authentication with bcrypt
- Comprehensive documentation and deployment guides"

# Push to GitHub
git branch -M main
git push -u origin main
```

### 5. Create Development Branch

```bash
# Create develop branch
git checkout -b develop
git push -u origin develop

# Set default branch to main in GitHub (Settings > Default branch)
```

## Ongoing Workflow

### Feature Development
```bash
# Create feature branch
git checkout -b feature/feature-name

# Make changes
# Commit frequently with clear messages
git commit -m "feat: add new feature description"

# Push feature branch
git push origin feature/feature-name

# Create Pull Request on GitHub
# - Use PR template if available
# - Link to issues with "Fixes #123"
- Request review

# After approval, merge to develop
git checkout develop
git pull origin develop
git merge --no-ff feature/feature-name
git push origin develop

# Delete feature branch
git branch -d feature/feature-name
git push origin --delete feature/feature-name
```

### Release Process
```bash
# Create release branch from develop
git checkout -b release/v1.0.0 develop

# Update version numbers if applicable
# Make release-only changes

# Commit release changes
git commit -m "release: version 1.0.0"

# Merge to main
git checkout main
git pull origin main
git merge --no-ff release/v1.0.0

# Create tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push main and tags
git push origin main
git push origin v1.0.0

# Merge back to develop
git checkout develop
git merge --no-ff release/v1.0.0
git push origin develop

# Delete release branch
git branch -d release/v1.0.0
git push origin --delete release/v1.0.0
```

## Commit Message Convention

Follow conventional commits:

```
<type>(<scope>): <subject>
<blank line>
<body>
<blank line>
<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Test additions/changes
- `chore`: Build/dependency updates
- `ci`: CI/CD changes
- `security`: Security improvements

### Examples
```bash
git commit -m "feat(options): add gamma exposure calculation"
git commit -m "fix(auth): resolve password verification issue"
git commit -m "docs: update deployment guide"
git commit -m "refactor: optimize API request handling"
git commit -m "security: migrate API keys to environment variables"
```

## GitHub Features Setup

### 1. Branch Protection (main)
Settings > Branches > main > Add rule
- [ ] Require a pull request before merging
- [ ] Require status checks to pass
- [ ] Require branches to be up to date
- [ ] Require code reviews: 1 approval
- [ ] Dismiss stale PR approvals
- [ ] Require status checks

### 2. Enable Wiki
Settings > Features > Wikis > Enabled
- Add documentation pages
- API reference
- Troubleshooting guide

### 3. Setup Discussions
Settings > Features > Discussions > Enabled
- Q&A category
- Ideas category
- Show in sidebar

### 4. Add Topics
Settings > Repository details > Topics
- `python`
- `streamlit`
- `financial-analysis`
- `options-trading`
- `market-scanner`
- `api-integration`

### 5. Add Funding
.github/FUNDING.yml
```yaml
patreon: yourusername
buy_me_a_coffee: yourusername
```

## Create Documentation Files

### GitHub Issues Template
Create `.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug Report
about: Report a bug
---

## Description
...

## Steps to Reproduce
...

## Expected Behavior
...

## Actual Behavior
...

## Environment
- Python version:
- Streamlit version:
- OS:
```

### Pull Request Template
Create `.github/PULL_REQUEST_TEMPLATE.md`:
```markdown
## Description
...

## Related Issues
Fixes #

## Changes Made
- ...

## Testing
- [ ] Tested locally
- [ ] No new warnings
- [ ] Verified .env not committed

## Checklist
- [ ] Code follows project style
- [ ] Updated documentation
- [ ] Added tests if needed
```

## Badges for README

Add to README.md:
```markdown
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Quality](https://github.com/yourusername/max-pain-analysis-public/workflows/Code%20Quality/badge.svg)](https://github.com/yourusername/max-pain-analysis-public/actions)
```

## Sync Local with Remote

```bash
# Fetch latest changes
git fetch origin

# See what's different
git status

# Pull latest changes from main branch
git pull origin main

# Push local changes
git push origin main
```

## Troubleshooting

### Push rejected because of .env
```bash
# Remove from git tracking
git rm --cached .env

# It's already in .gitignore, so won't be tracked again

# Commit the change
git commit -m "chore: remove .env from tracking"

# Push
git push origin main
```

### Large file accidentally committed
```bash
# Remove from history
git filter-branch --tree-filter 'rm -f path/to/file' HEAD

# Force push
git push origin main --force-with-lease
```

### Undo last commit (before push)
```bash
# Keep changes
git reset --soft HEAD~1

# Discard changes
git reset --hard HEAD~1
```

## GitHub Actions Status

Check build status:
- Go to Actions tab
- View workflow runs
- Click on run for details
- View logs

Troubleshooting failed builds:
1. Check error messages in logs
2. Verify all dependencies in requirements.txt
3. Check .gitignore didn't exclude needed files
4. Verify no .env file was committed

---

**Repository is now ready for GitHub! 🚀**
