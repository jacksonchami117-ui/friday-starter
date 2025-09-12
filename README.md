# Friday Martial Arts OS

![CI](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml/badge.svg)
![Coverage](./coverage.svg)
Setup instructions here.

### Timeline Editor (New)
- Drag assets into a video track, drag to reorder, resize to trim
- Text overlay track with inline editing (supports {{tokens}} for lead fields)
- Zoom & snapping feel; keyboard: arrows to nudge (Shift=1s), Delete to remove
- Save/Load manifest via `/campaigns/<cid>/manifest`
- Asset uploads at `/campaigns/<cid>/assets/upload` (video/image), thumbnails via ffmpeg

### Providers (optional)
Set these to enable notifications:
- `SENDGRID_API_KEY`, `EMAIL_FROM`
- `TWILIO_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM`

### Cleanup
- `CLEAN_DAYS` (default 14): outputs older than this are deleted daily.

## Deploy

There are two ways to deploy:

1) Manual run
- Go to Actions → "Deploy — App Runner (CI-only)" → Run workflow.

2) Chat/issue command
- Comment `/deploy` on any issue in this repo. A bot will trigger a deploy run.

Requirements (one-time)
- Org secret `GH_WORKFLOW_TOKEN` (scopes: repo + workflow).
- Org variables `AWS_REGION`, `AWS_ROLE_DEPLOY` (OIDC role ARN).
- Repo variable `ECR_REPOSITORY` (ECR repo name for this app).
- AWS IAM OIDC trust for the org: `token.actions.githubusercontent.com`, audience `sts.amazonaws.com`, subject `repo:jacksonchami117-ui/*:ref:refs/heads/main`.

See [ops/CI_README.md](ops/CI_README.md) for full setup details.
