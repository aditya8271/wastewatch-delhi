import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ─── CONFIG — fill these in .env or Streamlit secrets ───────────────────────
TWILIO_SID        = "ACf884b95a3bab3eeea1f44a1065eff65d"
TWILIO_AUTH       = "24424fac40a64b39ab0ce83b5691fc6b"
TWILIO_FROM       = "whatsapp:+14155238886"
ALERT_PHONE       = "whatsapp:+918572831710"

EMAIL_HOST        = os.getenv("EMAIL_HOST",  "smtp.gmail.com")
EMAIL_PORT        = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER        = os.getenv("EMAIL_USER",  "your@gmail.com")
EMAIL_PASS        = os.getenv("EMAIL_PASS",  "your_app_password")
ALERT_EMAIL       = os.getenv("ALERT_EMAIL", "officer@ludhiana.gov.in")
# ─────────────────────────────────────────────────────────────────────────────

def send_whatsapp_alert(dump_info: dict) -> tuple[bool, str]:
    """
    Send WhatsApp alert via Twilio sandbox.
    dump_info: dict with keys ward, severity, area_sqm, disease_risk, lat, lng
    """
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_AUTH)
        msg = (
            f"🚨 *ILLEGAL DUMP DETECTED*\n\n"
            f"📍 Ward: {dump_info.get('ward', 'Unknown')}\n"
            f"⚠️ Severity: {dump_info.get('severity', 'High')}\n"
            f"📐 Area: {dump_info.get('area_sqm', 0)} sq.m\n"
            f"🦟 Disease Risk: {dump_info.get('disease_risk', 'Unknown')}\n"
            f"🗺️ Location: {dump_info.get('lat', '')}, {dump_info.get('lng', '')}\n"
            f"🕐 Time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n\n"
            f"Please take immediate action."
        )
        message = client.messages.create(
            body=msg,
            from_=TWILIO_FROM,
            to=ALERT_PHONE
        )
        return True, f"WhatsApp sent! SID: {message.sid}"
    except ImportError:
        return False, "Twilio not installed. Run: pip install twilio"
    except Exception as e:
        return False, f"WhatsApp failed: {str(e)}"

def send_email_alert(dump_info: dict) -> tuple[bool, str]:
    """Send email alert to municipal officer"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 Illegal Dump Alert — {dump_info.get('ward', 'Unknown Ward')} | Severity: {dump_info.get('severity')}"
        msg["From"]    = EMAIL_USER
        msg["To"]      = ALERT_EMAIL

        html = f"""
        <html><body style="font-family:Arial,sans-serif;padding:20px">
          <div style="background:#E24B4A;color:white;padding:16px;border-radius:8px;margin-bottom:16px">
            <h2 style="margin:0">🚨 Illegal Dump Detected</h2>
            <p style="margin:4px 0 0">Delhi Waste Detection System</p>
          </div>
          <table style="width:100%;border-collapse:collapse">
            <tr style="background:#f5f5f5">
              <td style="padding:10px;font-weight:bold">Ward</td>
              <td style="padding:10px">{dump_info.get('ward','—')}</td>
            </tr>
            <tr>
              <td style="padding:10px;font-weight:bold">Severity</td>
              <td style="padding:10px;color:#E24B4A;font-weight:bold">{dump_info.get('severity','—')}</td>
            </tr>
            <tr style="background:#f5f5f5">
              <td style="padding:10px;font-weight:bold">Area</td>
              <td style="padding:10px">{dump_info.get('area_sqm',0)} sq. meters</td>
            </tr>
            <tr>
              <td style="padding:10px;font-weight:bold">Disease Risk</td>
              <td style="padding:10px;color:#D85A30">{dump_info.get('disease_risk','—')}</td>
            </tr>
            <tr style="background:#f5f5f5">
              <td style="padding:10px;font-weight:bold">Coordinates</td>
              <td style="padding:10px">{dump_info.get('lat','')}, {dump_info.get('lng','')}</td>
            </tr>
            <tr>
              <td style="padding:10px;font-weight:bold">Detected At</td>
              <td style="padding:10px">{datetime.now().strftime('%d %b %Y, %I:%M %p')}</td>
            </tr>
          </table>
          <div style="background:#EAF3DE;padding:14px;border-radius:8px;margin-top:16px">
            <strong>Action Required:</strong> Please assign a cleanup team immediately.
          </div>
        </body></html>
        """
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, ALERT_EMAIL, msg.as_string())
        return True, f"Email sent to {ALERT_EMAIL}"
    except Exception as e:
        return False, f"Email failed: {str(e)}"

def send_all_alerts(dump_info: dict) -> list[dict]:
    """Send both WhatsApp + email, return results list"""
    results = []
    ok1, msg1 = send_whatsapp_alert(dump_info)
    results.append({"channel": "WhatsApp", "success": ok1, "message": msg1})
    ok2, msg2 = send_email_alert(dump_info)
    results.append({"channel": "Email", "success": ok2, "message": msg2})
    return results
