from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Friday Starter is running ✅</h1><p>Go to <a href='/health'>/health</a> to check status.</p>"

@app.route("/health")
def health():
    return {"ok": True, "ts": datetime.utcnow().isoformat() + "Z"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)
