import os
import logging

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')

def notify_lead_rejected(user_email, lead_info):
    msg = f"Lead rejected: {lead_info}"
    if SENDGRID_API_KEY:
        # Implement SendGrid logic here (stub)
        pass
    else:
        logging.info(f"Notification (email): {msg}")

def notify_render_completed(user_email, job_info):
    msg = f"Render job completed: {job_info}"
    if SENDGRID_API_KEY:
        # Implement SendGrid logic here (stub)
        pass
    else:
        logging.info(f"Notification (email): {msg}")

def notify_sms(phone, message):
    if TWILIO_SID and TWILIO_TOKEN:
        # Implement Twilio logic here (stub)
        pass
    else:
        logging.info(f"Notification (SMS): {message}")