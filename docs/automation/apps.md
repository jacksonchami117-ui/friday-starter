# Automation and Integrations

This document makes installed tooling visible to both humans and automation (AIs, bots).

## Installed/Planned

- Dependabot — Config at `.github/dependabot.yml`. Creates update PRs for npm, Docker, and Actions.
- CodeQL — Workflow at `.github/workflows/codeql.yml`. Runs code scanning on push/PR.
- Snyk — Install the GitHub App and set `SNYK_TOKEN`. Workflow at `.github/workflows/snyk.yml`.
- GitHub Deploy Notifier — Posts a comment on PR or commit when deploy completes. Workflow at `.github/workflows/notify-deploy-github.yml`.

A machine-readable manifest is kept at `.github/ai-integrations.json` so other AIs can programmatically detect capabilities.

## Required Secrets/Variables

- Secrets:
  - `SNYK_TOKEN` — enables Snyk scans.
- Variables:
  - `AWS_REGION`, `ECR_REPOSITORY`, `AWS_ROLE_DEPLOY` — used by the App Runner deploy workflow.

## Notes

- All new checks are non-blocking by default (to keep velocity high). Tighten gates later as needed.
- Notifications use GitHub comments instead of Slack.