# FRIDAY Instructions (Ops Manual)

FRIDAY is a modular Flask system for personalized video outreach.

---

## Core Modules
- **Leads** — upload CSV/XLSX, validate, split accepted vs rejected
- **Editor** — drag/drop segments, save template manifest
- **Render** — generate personalized videos per lead (FFmpeg)
- **Exports** — Instantly/Smartlead CSV + batch ZIPs
- **Diagnostics** — package logs/CSVs for debugging

---

## Deployment

### Local
```bash
pip install -r requirements.txt
sudo apt-get install -y ffmpeg
python app.py
