"""
send_email.py - Automated Caretaker Notification Engine
Provides secure SMTP dispatching and fallback logging for patient vitals alerts.
"""

import os
import smtplib
import json
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ALERTS_LOG_PATH = os.path.join(DATA_DIR, "alerts_log.json")

# SMTP Configuration with sensible defaults
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_SENDER_EMAIL = os.getenv("ALERT_SENDER_EMAIL", SMTP_USERNAME or "alerts@bytelife.ai")
DEFAULT_CARETAKER_EMAIL = os.getenv("DEFAULT_CARETAKER_EMAIL", "caretaker@bytelife.ai")


def log_alert_to_file(alert_record):
    """Persist alert records to structured JSON file for auditing and UI review."""
    os.makedirs(DATA_DIR, exist_ok=True)
    logs = []
    if os.path.exists(ALERTS_LOG_PATH):
        try:
            with open(ALERTS_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    
    logs.insert(0, alert_record) # prepend most recent
    # Keep up to 100 historical alerts
    logs = logs[:100]

    with open(ALERTS_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)


def get_alert_history():
    """Retrieve historical caretaker alerts."""
    if os.path.exists(ALERTS_LOG_PATH):
        try:
            with open(ALERTS_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def format_remedies_html(remedies):
    """Format remedies list into styled HTML list."""
    if not remedies:
        return "<li>Follow standard resting protocols and consult attending physician.</li>"
    html_items = ""
    for r in remedies:
        html_items += f"<li style='margin-bottom: 6px;'><strong>{r.get('title', 'Action')}:</strong> {r.get('description', '')}</li>"
    return html_items


def format_remedies_text(remedies):
    """Format remedies list into plain text."""
    if not remedies:
        return "- Follow standard resting protocols and consult physician.\n"
    text_items = ""
    for r in remedies:
        text_items += f"- {r.get('title', 'Action')}: {r.get('description', '')}\n"
    return text_items


def send_caretaker_alert(
    patient_name="Senior Care Patient",
    vitals=None,
    alert_level="Critical",
    recipient_email=None,
    remedies=None,
    rule_overrides=None,
    override_reason=None
):
    """
    Dispatches automated caretaker notification.
    If SMTP server credentials are valid, sends live email via TLS.
    Otherwise gracefully falls back to structured local simulation mode, 
    persisting the record to data/alerts_log.json.
    """
    vitals = vitals or {}
    remedies = remedies or []
    rule_overrides = rule_overrides or []
    recipient = recipient_email if (recipient_email and "@" in recipient_email) else DEFAULT_CARETAKER_EMAIL
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_id = f"ALERT-{uuid.uuid4().hex[:8].upper()}"

    is_critical = (alert_level.upper() == "CRITICAL")
    badge_color = "#e53e3e" if is_critical else "#dd6b20"
    subject = f"[{alert_level.upper()} HEALTH ALERT] Patient Vitals Anomaly: {patient_name} - {timestamp}"

    # Build plain text fallback
    body_text = f"""
=====================================================
BYTELIFE CORE - CARETAKER ALERT NOTIFICATION
=====================================================
Patient: {patient_name}
Status Level: {alert_level.upper()}
Timestamp: {timestamp}
Alert Reference: {message_id}

CURRENT RECORDED VITALS:
- Heart Rate: {vitals.get('heart_rate', 'N/A')} bpm
- Blood Pressure: {vitals.get('systolic_bp', 'N/A')}/{vitals.get('diastolic_bp', 'N/A')} mmHg
- SpO2 (Oxygen Saturation): {vitals.get('spo2', 'N/A')}%
- Body Temperature: {vitals.get('temperature', 'N/A')} °F

SAFETY OVERRIDES:
{override_reason if override_reason else 'None (ML classification matched clinical safety ranges)'}

RECOMMENDED FIRST-AID / OVER-THE-COUNTER REMEDIES:
{format_remedies_text(remedies)}

URGENT NOTICE:
{'Please dispatch immediate medical attention or call emergency services (911/112).' if is_critical else 'Please monitor patient closely and follow up if vitals do not stabilize within 30 minutes.'}
=====================================================
"""

    # Build rich HTML email
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>{subject}</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f7fafc; margin: 0; padding: 20px; color: #2d3748;">
      <div style="max-width: 620px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        
        <!-- Header Banner -->
        <div style="background-color: {badge_color}; color: #ffffff; padding: 20px; text-align: center;">
          <h1 style="margin: 0; font-size: 24px; letter-spacing: 0.5px;">ByteLife Automated Alert</h1>
          <p style="margin: 5px 0 0; font-size: 16px; font-weight: bold; text-transform: uppercase;">Status: {alert_level}</p>
        </div>

        <div style="padding: 24px;">
          <p style="font-size: 16px; line-height: 1.5; margin-top: 0;">
            This is an automated safety alert for <strong>{patient_name}</strong> recorded at <strong>{timestamp}</strong>.
          </p>

          <!-- Vitals Summary Table -->
          <h3 style="color: #2b6cb0; border-bottom: 2px solid #edf2f7; padding-bottom: 8px; margin-top: 20px;">
            Patient Physiological Vitals
          </h3>
          <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 15px;">
            <thead>
              <tr style="background-color: #edf2f7; text-align: left;">
                <th style="padding: 10px; border: 1px solid #e2e8f0;">Metric</th>
                <th style="padding: 10px; border: 1px solid #e2e8f0;">Recorded Value</th>
                <th style="padding: 10px; border: 1px solid #e2e8f0;">Standard Range</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="padding: 10px; border: 1px solid #e2e8f0;">Heart Rate</td>
                <td style="padding: 10px; border: 1px solid #e2e8f0; font-weight: bold;">{vitals.get('heart_rate', 'N/A')} bpm</td>
                <td style="padding: 10px; border: 1px solid #e2e8f0; color: #718096;">60 - 100 bpm</td>
              </tr>
              <tr style="background-color: #f7fafc;">
                <td style="padding: 10px; border: 1px solid #e2e8f0;">Blood Pressure</td>
                <td style="padding: 10px; border: 1px solid #e2e8f0; font-weight: bold;">{vitals.get('systolic_bp', 'N/A')} / {vitals.get('diastolic_bp', 'N/A')} mmHg</td>
                <td style="padding: 10px; border: 1px solid #e2e8f0; color: #718096;">90-120 / 60-80 mmHg</td>
              </tr>
              <tr>
                <td style="padding: 10px; border: 1px solid #e2e8f0;">SpO2 (Oxygen)</td>
                <td style="padding: 10px; border: 1px solid #e2e8f0; font-weight: bold;">{vitals.get('spo2', 'N/A')}%</td>
                <td style="padding: 10px; border: 1px solid #e2e8f0; color: #718096;">95% - 100%</td>
              </tr>
              <tr style="background-color: #f7fafc;">
                <td style="padding: 10px; border: 1px solid #e2e8f0;">Body Temperature</td>
                <td style="padding: 10px; border: 1px solid #e2e8f0; font-weight: bold;">{vitals.get('temperature', 'N/A')} °F</td>
                <td style="padding: 10px; border: 1px solid #e2e8f0; color: #718096;">97.0°F - 99.0°F</td>
              </tr>
            </tbody>
          </table>

          {f'''
          <div style="background-color: #fffaf0; border-left: 4px solid #dd6b20; padding: 12px; margin-bottom: 20px; font-size: 14px;">
            <strong>Failsafe Rule Trigger:</strong> {override_reason}
          </div>
          ''' if override_reason else ''}

          <!-- Recommended Remedies -->
          <h3 style="color: #2b6cb0; border-bottom: 2px solid #edf2f7; padding-bottom: 8px;">
            Recommended Immediate Actions & OTC Remedies
          </h3>
          <ul style="padding-left: 20px; line-height: 1.6; font-size: 14px;">
            {format_remedies_html(remedies)}
          </ul>

          <!-- Call to action / Hotline -->
          <div style="background-color: {'#fed7d7' if is_critical else '#feebc8'}; border: 1px solid {'#feb2b2' if is_critical else '#fbd38d'}; border-radius: 6px; padding: 16px; margin-top: 24px; text-align: center;">
            <p style="margin: 0; font-size: 15px; font-weight: bold; color: {'#9b2c2c' if is_critical else '#7b341e'};">
              {'EMERGENCY: Immediate clinical intervention required. Contact emergency hotline (911 / 112).' if is_critical else 'ATTENTION: Monitor vital trends closely over the next 30 minutes.'}
            </p>
          </div>

          <p style="font-size: 12px; color: #a0aec0; margin-top: 24px; text-align: center;">
            Ref: {message_id} | ByteLife Core - Elderly & Career Intelligence Hub
          </p>
        </div>
      </div>
    </body>
    </html>
    """

    alert_record = {
        "message_id": message_id,
        "patient_name": patient_name,
        "recipient": recipient,
        "sender": ALERT_SENDER_EMAIL,
        "timestamp": timestamp,
        "alert_level": alert_level,
        "vitals": vitals,
        "override_reason": override_reason,
        "remedies": remedies,
        "subject": subject
    }

    # Check if live SMTP credentials are provided
    can_attempt_smtp = bool(SMTP_USERNAME and SMTP_PASSWORD and SMTP_USERNAME != "your_email@gmail.com")

    if can_attempt_smtp:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = ALERT_SENDER_EMAIL
            msg["To"] = recipient

            part1 = MIMEText(body_text, "plain", "utf-8")
            part2 = MIMEText(body_html, "html", "utf-8")
            msg.attach(part1)
            msg.attach(part2)

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(ALERT_SENDER_EMAIL, [recipient], msg.as_string())

            alert_record["status"] = "SENT_SMTP"
            alert_record["mode"] = "live_smtp"
            log_alert_to_file(alert_record)

            return {
                "success": True,
                "mode": "live_smtp",
                "message_id": message_id,
                "recipient": recipient,
                "timestamp": timestamp,
                "alert_level": alert_level,
                "subject": subject,
                "message": f"Live email alert successfully sent to {recipient}"
            }
        except Exception as e:
            alert_record["status"] = f"SMTP_FAILED_FALLBACK_SIMULATED: {str(e)}"
            alert_record["mode"] = "simulated_fallback"
            log_alert_to_file(alert_record)

            return {
                "success": True,
                "mode": "simulated_fallback",
                "message_id": message_id,
                "recipient": recipient,
                "timestamp": timestamp,
                "alert_level": alert_level,
                "subject": subject,
                "message": f"SMTP network failed ({str(e)}). Notification recorded securely to system audit log.",
                "preview_text": body_text
            }
    else:
        # Graceful simulated delivery (local test / staging mode)
        alert_record["status"] = "SIMULATED_DISPATCH"
        alert_record["mode"] = "simulated_dispatch"
        log_alert_to_file(alert_record)

        return {
            "success": True,
            "mode": "simulated_dispatch",
            "message_id": message_id,
            "recipient": recipient,
            "timestamp": timestamp,
            "alert_level": alert_level,
            "subject": subject,
            "message": f"Simulated Caretaker Alert logged for {recipient} (Configure SMTP in .env for live emails)",
            "preview_text": body_text
        }


if __name__ == "__main__":
    print("Testing Caretaker Alert Dispatch...")
    sample_vitals = {
        "heart_rate": 138,
        "systolic_bp": 185,
        "diastolic_bp": 115,
        "spo2": 88.5,
        "temperature": 102.8
    }
    sample_remedies = [
        {"title": "Oxygen Support", "description": "Administer supplemental O2 and position patient upright."},
        {"title": "Call Emergency", "description": "Dispatch emergency ambulance immediately (BP crisis & hypoxemia)."}
    ]
    res = send_caretaker_alert(
        patient_name="Pranith Kumar",
        vitals=sample_vitals,
        alert_level="Critical",
        recipient_email="caretaker@bytelife.ai",
        remedies=sample_remedies,
        override_reason="SpO2 < 90% and Systolic BP >= 180 mmHg"
    )
    print(json.dumps(res, indent=2))
