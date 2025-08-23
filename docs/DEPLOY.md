# FRIDAY Deployment Guide

## Git LFS Setup
- Install git-lfs: `apt-get install -y git-lfs`
- Run `git lfs install && git lfs pull` before pip/npm.

## Build & Deploy
- Run `npm install && npm run build` before deploy.
- Use Gunicorn as entrypoint: `gunicorn app:app --workers=1 --threads=4 --timeout=120`
- Mount persistent /data for STATE_DIR.

## Housekeeping
- Old state/outputs/videos (>3 days) deleted at startup.

## CI/CD
- GitHub Actions: LFS + npm build + pytest + artifact upload.

## Cache Busting
- Asset URLs include ?v=<timestamp> for cache busting.

## Smoke Test
- See tests/smoke_test.py for intro and asset checks.
