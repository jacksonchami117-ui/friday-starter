# Testing & Smoke — FRIDAY Starter

## Local Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ADMIN_PASSWORD=admin
python app.py
# open http://localhost:10000
```

Quick Manual Test

Visit /auth/login and login with ADMIN_PASSWORD.

Go to /editor, drag-drop a short video (or click to upload).

Add the uploaded asset to the timeline (click its list item).

(Optional) Add a Text Overlay.

Click Save Manifest or directly Start Render.

Check Dashboard for your job progress; open the Output once done.

Automated Smoke Test
export BASE_URL=http://localhost:10000
export ADMIN_PASSWORD=admin
python scripts/smoke_test.py

The smoke test:

Generates a 1s color clip via ffmpeg

Uploads it via /editor/upload

Starts a render via /render/start

Polls /render/status/<id> until done

Fails if job fails or times out
