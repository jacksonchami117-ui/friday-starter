# 🚀 COMPLETE FRIDAY STARTER SETUP GUIDE

## 📍 CRITICAL: Correct Workspace Location
**ALWAYS START HERE:** `/Users/jacksonn/Documents/GitHub/friday-starter`

### ❌ WRONG LOCATIONS (DO NOT USE):
- `/Applications/Maxon Cinema 4D R22/resource/osx/cursors` (Cinema 4D folder)
- Any system directories or unrelated paths

### ✅ VERIFICATION COMMANDS:
```bash
# Navigate to correct location
cd ~/Documents/GitHub/friday-starter

# Verify you're in the right place
pwd
ls -la .github/workflows/  # Should show deploy_apprunner.yml
ls -la app.py              # Should exist
ls -la Dockerfile          # Should exist
ls -la requirements.txt    # Should exist
```

---

## 🔐 AUTHENTICATION TOKENS & SECRETS

### GitHub Personal Access Token:
**Note:** The actual token is stored securely and should be retrieved from the user when needed.

### Repository Variables (CONFIGURED):
- `AWS_REGION`: `ap-southeast-2`
- `AWS_ROLE_DEPLOY`: `arn:aws:iam::454842420292:role/FridayDeployRole`
- `AWS_APPRUNNER_ECR_ACCESS_ROLE`: `arn:aws:iam::454842420292:role/FridayAppRunnerECRAccess`
- `ECR_REPOSITORY`: `friday-starter`
- `ECR_REGISTRY`: `454842420292.dkr.ecr.ap-southeast-2.amazonaws.com`
- `AI_OWNER`: `jacksonchami117-ui`
- `AI_REPO`: `friday-starter`

---

## 🏗️ COMPLETE PROJECT STRUCTURE

```
/Users/jacksonn/Documents/GitHub/friday-starter/
├── .github/
│   ├── workflows/
│   │   ├── deploy_apprunner.yml          # Main deployment workflow
│   │   ├── command_deploy.yml            # /deploy command handler
│   │   ├── ci.yml                        # Continuous integration
│   │   ├── smoke.yml                     # Smoke tests
│   │   ├── auto_fixer.yml                # Self-healing system
│   │   ├── live_monitoring.yml           # Real-time status updates
│   │   ├── photo_feedback.yml            # Screenshot automation
│   │   ├── synthetic_user.yml            # User simulation
│   │   ├── live_e2e.yml                  # End-to-end testing
│   │   ├── qa_lighthouse.yml             # Performance testing
│   │   └── [20+ other workflows]         # Complete automation suite
│   └── settings.yml                      # Repository configuration
├── src/                                  # Application source code
├── templates/                            # Flask templates
├── static/                               # Static assets
├── tests/                                # Test suite
│   └── e2e/                              # Playwright E2E tests
├── ops/                                  # Operations documentation
│   ├── context.yaml                      # AWS context
│   ├── AI_ACCESS.md                      # AI setup guide
│   ├── CI_README.md                      # CI/CD documentation
│   └── RUNBOOK.md                        # Operational procedures
├── scripts/                              # Automation scripts
│   ├── auto_fixer.py                     # Self-healing logic
│   └── state_manager.py                  # State management
├── app.py                                # Main Flask application
├── Dockerfile                            # Container configuration
├── requirements.txt                      # Python dependencies
├── agent_policy.yaml                     # AI agent permissions
├── qc_policy.yaml                        # Quality control rules
├── TASKS.md                              # Task tracking
├── AGENT_MANDATE.md                      # Agent operating instructions
└── COMPLETE_SETUP_GUIDE.md               # This file
```

---

## 🚀 DEPLOYMENT SYSTEM

### Current Status:
- ✅ All AWS variables configured
- ✅ GitHub App authentication set up
- ✅ OIDC roles configured
- ✅ ECR repository ready
- ⚠️ Deployments currently being skipped (needs diagnosis)

### Deployment Methods:
1. **Automatic**: Push to `main` branch
2. **Manual**: GitHub Actions "Run workflow" button
3. **Slash Command**: Comment `/deploy` on any issue

### Expected Live URL Pattern:
```
https://[service-name]-[account-id].[region].awsapprunner.com
```

---

## 🔧 TROUBLESHOOTING COMMANDS

### Check Deployment Status:
```bash
# Check latest workflow runs (replace TOKEN with actual token)
curl -s -H "Authorization: token TOKEN" \
  "https://api.github.com/repos/jacksonchami117-ui/friday-starter/actions/runs?per_page=5"

# Check repository variables (replace TOKEN with actual token)
curl -s -H "Authorization: token TOKEN" \
  "https://api.github.com/repos/jacksonchami117-ui/friday-starter/actions/variables"

# Trigger deployment (replace TOKEN with actual token)
curl -X POST -H "Authorization: token TOKEN" \
  "https://api.github.com/repos/jacksonchami117-ui/friday-starter/dispatches" \
  -d '{"event_type": "deploy"}'
```

### Post Deploy Command:
```bash
# Comment /deploy on Issue #1 (replace TOKEN with actual token)
curl -X POST -H "Authorization: token TOKEN" \
  "https://api.github.com/repos/jacksonchami117-ui/friday-starter/issues/1/comments" \
  -d '{"body": "/deploy"}'
```

---

## 🎯 QUICK START CHECKLIST

1. **Navigate to correct directory**: `cd ~/Documents/GitHub/friday-starter`
2. **Verify location**: Run `./quick_check.sh` (if available)
3. **Check deployment status**: Look at GitHub Actions runs
4. **Trigger deployment**: Use `/deploy` comment or manual dispatch
5. **Monitor progress**: Watch for live URL in GitHub Actions or issues

---

## 🚨 CRITICAL REMINDERS

- **NEVER** work in Cinema 4D directories
- **ALWAYS** verify workspace location first
- **USE** the GitHub token for API calls (retrieve from user when needed)
- **CHECK** all variables are configured before deploying
- **MONITOR** deployment progress through GitHub Actions

---

*This guide contains all the information needed to work with the Friday Starter project autonomously.*
