from __future__ import annotations
import os
from flask import Blueprint, render_template, request, jsonify
from .notify import send_email, send_sms, send_slack, send_webhook

bp = Blueprint("settings", __name__, url_prefix="/settings")

def _status(name, *envs):
    ok = all(os.environ.get(e) for e in envs)
    return {"name": name, "configured": ok, "env": ", ".join(envs)}

@bp.route("/", methods=["GET"])
def index():
    return settings_home()

@bp.route("/", methods=["GET"])
def settings_home():
    providers = [
        _status("SendGrid Email", "SENDGRID_API_KEY", "EMAIL_FROM"),
        _status("Twilio SMS", "TWILIO_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM"),
        _status("Slack Webhook", "SLACK_WEBHOOK_URL"),
        _status("Custom Webhook", "CUSTOM_WEBHOOK_URL"),
    ]
    return render_template("settings.html", providers=providers)

@bp.route("/test/email", methods=["POST"])
def test_email():
    to = request.form.get("to")
    if not to: return jsonify({"ok": False, "error": "Missing 'to'"}), 400
    res = send_email(to, "FRIDAY test email", "Your FRIDAY email settings work!")
    return jsonify(res)

@bp.route("/test/sms", methods=["POST"])
def test_sms():
    to = request.form.get("to")
    if not to: return jsonify({"ok": False, "error": "Missing 'to'"}), 400
    res = send_sms(to, "Your FRIDAY SMS settings work!")
    return jsonify(res)

@bp.route("/test/slack", methods=["POST"])
def test_slack():
    res = send_slack("🧪 Test notification from FRIDAY settings page")
    return jsonify(res)

@bp.route("/test/webhook", methods=["POST"])
def test_webhook():
    test_data = {
        "event": "test",
        "message": "Test webhook from FRIDAY settings page",
        "source": "settings_test"
    }
    res = send_webhook(test_data)
    return jsonify(res)
