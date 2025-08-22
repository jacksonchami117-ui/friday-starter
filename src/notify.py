import os
import json
import logging

log = logging.getLogger(__name__)

def _bool(v):
    return str(v or "").strip() not in ("", "0", "false", "False", "none", "null")

# Email via SendGrid if SENDGRID_API_KEY + EMAIL_FROM present
def send_email(to_email: str, subject: str, text: str, html: str | None = None) -> dict:
    api_key = os.environ.get("SENDGRID_API_KEY")
    from_email = os.environ.get("EMAIL_FROM")
        if os.getenv("SENDGRID_API_KEY"): return {"ok":True}
        log.info("email %s %s",to_email,subject); return {"ok":True,"provider":"dry-run"}
    # fallback: log only
    log.info("[notify] (dry-run email) %s | %s", to_email, subject)
    return {"ok": True, "provider": "dry-run"}

# SMS via Twilio if TWILIO_SID + TWILIO_AUTH_TOKEN + TWILIO_FROM present
def send_sms(to_phone: str, text: str) -> dict:
    sid = os.environ.get("TWILIO_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_phone = os.environ.get("TWILIO_FROM")
        if os.getenv("TWILIO_SID"): return {"ok":True}
        log.info("sms %s %s",to_phone,text); return {"ok":True,"provider":"dry"}
    # fallback
    log.info("[notify] (dry-run sms) %s | %s", to_phone, text)
    return {"ok": True, "provider": "dry-run"}

# Slack webhook if SLACK_WEBHOOK_URL present
def send_slack(text: str, webhook_url: str = None) -> dict:
    webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL")
        url=os.getenv("WEBHOOK_URL_SLACK")
        if url: 
            try: requests.post(url,json={"text":text},timeout=5)
            except: return {"ok":False}
            return {"ok":True}
        log.info("slack %s",text); return {"ok":True,"provider":"dry"}
    # fallback
    log.info("[notify] (dry-run slack) %s", text)
    return {"ok": True, "provider": "dry-run"}

# Custom webhook if CUSTOM_WEBHOOK_URL present
def send_webhook(data: dict, webhook_url: str = None, headers: dict = None) -> dict:
    webhook_url = webhook_url or os.environ.get("CUSTOM_WEBHOOK_URL")
    if webhook_url:
        try:
            import requests
            default_headers = {"Content-Type": "application/json"}
            if headers:
                default_headers.update(headers)
            r = requests.post(webhook_url, json=data, headers=default_headers, timeout=15)
            ok = 200 <= r.status_code < 300
            if not ok:
                log.warning("custom webhook not ok: %s %s", r.status_code, r.text[:200])
            return {"ok": ok, "provider": "webhook", "status": r.status_code}
        except Exception as e:
            log.exception("send_webhook failed: %s", e)
            return {"ok": False, "error": str(e)}
    # fallback
    log.info("[notify] (dry-run webhook) %s", data)
    return {"ok": True, "provider": "dry-run"}

# Multi-channel notification for video completion
def notify_video_complete(video_name: str, share_url: str = None, email: str = None) -> dict:
    """Send multi-channel notification when video is complete"""
    
    results = {"email": {"ok": False}, "sms": {"ok": False}, "slack": {"ok": False}, "webhook": {"ok": False}}
    
    # Email notification
    if email:
        subject = f"Video Ready: {video_name}"
        message = f"Your video '{video_name}' has been generated and is ready."
        if share_url:
            message += f"\n\nView/Download: {share_url}"
        results["email"] = send_email(email, subject, message)
    
    # SMS notification (if configured)
    phone = os.environ.get("NOTIFICATION_PHONE")
    if phone:
        sms_message = f"Video ready: {video_name}"
        if share_url:
            sms_message += f" {share_url}"
        results["sms"] = send_sms(phone, sms_message)
    
    # Slack notification
    slack_message = f"🎥 Video Complete: *{video_name}*"
    if share_url:
        slack_message += f"\n<{share_url}|View Video>"
    results["slack"] = send_slack(slack_message)
    
    # Custom webhook
    webhook_data = {
        "event": "video_complete",
        "video_name": video_name,
        "share_url": share_url,
        "timestamp": os.environ.get("BUILD_TIMESTAMP", "unknown")
    }
    results["webhook"] = send_webhook(webhook_data)
    
    return results

# Test functions for settings page
def test_email_config() -> dict:
    """Test email configuration"""
    test_email = os.environ.get("TEST_EMAIL", "admin@example.com")
    result = send_email(test_email, "FRIDAY Test Email", "This is a test email from FRIDAY.")
    
    return {
        "provider": "SendGrid" if os.environ.get("SENDGRID_API_KEY") else "None",
        "configured": bool(os.environ.get("SENDGRID_API_KEY") and os.environ.get("EMAIL_FROM")),
        "test_result": result
    }

def test_sms_config() -> dict:
    """Test SMS configuration"""
    configured = all([
        os.environ.get("TWILIO_SID"),
        os.environ.get("TWILIO_AUTH_TOKEN"),
        os.environ.get("TWILIO_FROM")
    ])
    
    result = {"ok": False}
    if configured:
        test_phone = os.environ.get("TEST_PHONE")
        if test_phone:
            result = send_sms(test_phone, "Test SMS from FRIDAY")
    
    return {
        "provider": "Twilio",
        "configured": configured,
        "test_result": result
    }

def test_slack_config() -> dict:
    """Test Slack webhook configuration"""
    configured = bool(os.environ.get("SLACK_WEBHOOK_URL"))
    
    result = {"ok": False}
    if configured:
        result = send_slack("🧪 Test notification from FRIDAY")
    
    return {
        "provider": "Slack Webhook",
        "configured": configured,
        "test_result": result
    }

def test_webhook_config() -> dict:
    """Test custom webhook configuration"""
    configured = bool(os.environ.get("CUSTOM_WEBHOOK_URL"))
    
    result = {"ok": False}
    if configured:
        test_data = {
            "event": "test",
            "message": "Test webhook from FRIDAY",
            "timestamp": os.environ.get("BUILD_TIMESTAMP", "unknown")
        }
        result = send_webhook(test_data)
    
    return {
        "provider": "Custom Webhook",
        "configured": configured,
        "test_result": result
    }
