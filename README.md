# FRIDAY Hub UI (Flask on Render)

Flask-based FRIDAY Hub with cinematic intro and dashboard.

## Local dev
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=app.py                             # Windows: set FLASK_APP=app.py
flask run
# open http://127.0.0.1:5000
```

## Render
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
- Environment: Python 3.11+
