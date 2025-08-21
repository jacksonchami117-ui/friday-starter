import os, json, requests

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM = os.getenv("SENDGRID_FROM")
SENDGRID_TO = os.getenv("SENDGRID_TO")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_TO = os.getenv("TWILIO_TO")

def email(subject: str, body: str):
    if not (SENDGRID_API_KEY and SENDGRID_FROM and SENDGRID_TO):
        return False
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"}
    data = {
        "personalizations": [{"to": [{"email": SENDGRID_TO}], "subject": subject}],
        "from": {"email": SENDGRID_FROM},
        "content": [{"type": "text/plain", "value": body}],
    }
    r = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
    return r.status_code in (200, 202)

def sms(body: str):
    if not (TWILIO_SID and TWILIO_AUTH and TWILIO_FROM and TWILIO_TO):
        return False
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    data = {"From": TWILIO_FROM, "To": TWILIO_TO, "Body": body}
    r = requests.post(url, data=data, auth=(TWILIO_SID, TWILIO_AUTH), timeout=10)
    return r.status_code in (200, 201)
