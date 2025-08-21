import os
import logging
from flask import Blueprint, session, request, jsonify

notify_bp = Blueprint("notify", __name__, url_prefix="/notify")

# Environment-configurable notification settings
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "smtp")  # smtp, sendgrid, etc.
SMS_PROVIDER = os.getenv("SMS_PROVIDER", "twilio")  # twilio, aws-sns, etc.
NOTIFICATIONS_ENABLED = os.getenv("NOTIFICATIONS_ENABLED", "1") == "1"

# Notification stubs
def send_email_notification(to_email, subject, message, template=None):
    """
    Email notification stub - environment configurable
    """
    if not NOTIFICATIONS_ENABLED:
        logging.info(f"Notifications disabled - would send email to {to_email}: {subject}")
        return {"status": "disabled", "message": "Notifications are disabled"}
    
    logging.info(f"EMAIL STUB [{EMAIL_PROVIDER}] TO: {to_email}, SUBJECT: {subject}")
    
    # Implementation would depend on EMAIL_PROVIDER
    if EMAIL_PROVIDER == "smtp":
        return _send_smtp_email(to_email, subject, message, template)
    elif EMAIL_PROVIDER == "sendgrid":
        return _send_sendgrid_email(to_email, subject, message, template)
    else:
        logging.warning(f"Unsupported email provider: {EMAIL_PROVIDER}")
        return {"status": "error", "message": "Unsupported email provider"}

def send_sms_notification(to_phone, message):
    """
    SMS notification stub - environment configurable
    """
    if not NOTIFICATIONS_ENABLED:
        logging.info(f"Notifications disabled - would send SMS to {to_phone}: {message}")
        return {"status": "disabled", "message": "Notifications are disabled"}
    
    logging.info(f"SMS STUB [{SMS_PROVIDER}] TO: {to_phone}, MESSAGE: {message}")
    
    # Implementation would depend on SMS_PROVIDER
    if SMS_PROVIDER == "twilio":
        return _send_twilio_sms(to_phone, message)
    elif SMS_PROVIDER == "aws-sns":
        return _send_aws_sns_sms(to_phone, message)
    else:
        logging.warning(f"Unsupported SMS provider: {SMS_PROVIDER}")
        return {"status": "error", "message": "Unsupported SMS provider"}

# Provider-specific stubs
def _send_smtp_email(to_email, subject, message, template=None):
    """SMTP email implementation stub"""
    # Would implement SMTP logic here
    return {"status": "stub", "provider": "smtp", "to": to_email}

def _send_sendgrid_email(to_email, subject, message, template=None):
    """SendGrid email implementation stub"""
    # Would implement SendGrid API logic here
    return {"status": "stub", "provider": "sendgrid", "to": to_email}

def _send_twilio_sms(to_phone, message):
    """Twilio SMS implementation stub"""
    # Would implement Twilio API logic here
    return {"status": "stub", "provider": "twilio", "to": to_phone}

def _send_aws_sns_sms(to_phone, message):
    """AWS SNS SMS implementation stub"""
    # Would implement AWS SNS logic here
    return {"status": "stub", "provider": "aws-sns", "to": to_phone}

# Flask routes for notification management
@notify_bp.route("/toggle", methods=["POST"])
def toggle_notifications():
    """Toggle notifications for current session"""
    current_state = session.get("notifications_enabled", True)
    new_state = not current_state
    session["notifications_enabled"] = new_state
    
    return jsonify({
        "status": "success",
        "notifications_enabled": new_state,
        "message": f"Notifications {'enabled' if new_state else 'disabled'}"
    })

@notify_bp.route("/status", methods=["GET"])
def notification_status():
    """Get current notification status"""
    session_enabled = session.get("notifications_enabled", True)
    global_enabled = NOTIFICATIONS_ENABLED
    
    return jsonify({
        "session_enabled": session_enabled,
        "global_enabled": global_enabled,
        "effective_enabled": session_enabled and global_enabled,
        "email_provider": EMAIL_PROVIDER,
        "sms_provider": SMS_PROVIDER
    })

@notify_bp.route("/test", methods=["POST"])
def test_notification():
    """Test notification functionality"""
    data = request.get_json() or {}
    notification_type = data.get("type", "email")
    
    if notification_type == "email":
        result = send_email_notification(
            to_email=data.get("to_email", "test@example.com"),
            subject="FRIDAY Test Notification",
            message="This is a test notification from FRIDAY system."
        )
    elif notification_type == "sms":
        result = send_sms_notification(
            to_phone=data.get("to_phone", "+1234567890"),
            message="FRIDAY test SMS notification"
        )
    else:
        return jsonify({"status": "error", "message": "Invalid notification type"}), 400
    
    return jsonify(result)

# Helper function to check if notifications are enabled for session
def should_notify():
    """Check if notifications should be sent based on session and global settings"""
    return NOTIFICATIONS_ENABLED and session.get("notifications_enabled", True)