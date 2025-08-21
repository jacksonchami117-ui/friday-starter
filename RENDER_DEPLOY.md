# Render Deploy — FRIDAY Starter

## Prereqs
- Repo: `jacksonchami117-ui/friday-starter`
- `render.yaml` present at repo root
- App uses Gunicorn and installs `ffmpeg` at build time

## Steps
1) **Create a new Web Service** on Render and connect this repo.
2) Render reads `render.yaml`:
   - Installs `ffmpeg` and Python deps
   - Starts `gunicorn` on **$PORT**
   - Mounts persistent disk at **/data** with **STATE_DIR=/data/state**
3) **Set env vars** in Render:
   - `ADMIN_PASSWORD` (required)
   - `STATE_DIR=/data/state`
   - `USE_DB=1`
   - Optional: `API_KEY`, SendGrid/Twilio keys
4) **Deploy** and watch logs.
5) **Validate**:
   - Hit `/healthz` → `{ "ok": true }`
   - Login `/auth/login` with `ADMIN_PASSWORD`
   - Upload a short clip in **Editor**
   - Start render and confirm MP4 + thumbnail in **state/outputs**.

### Notes
- Gunicorn is configured as one worker (`-w 1`) with threads to avoid duplicate render workers.
- If you need horizontal scale for rendering, use a separate worker process/worker dyno pattern later (Celery/RQ).
