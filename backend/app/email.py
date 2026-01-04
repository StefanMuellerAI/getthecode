"""Email service for sending verification codes.

Handles SMTP-based email sending for the Double Opt-In verification process.
"""
import logging
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def generate_verification_code() -> str:
    """Generate a 6-digit numeric verification code."""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(to_email: str, code: str) -> bool:
    """
    Send a verification code email.
    
    Args:
        to_email: Recipient email address
        code: 6-digit verification code
        
    Returns:
        True if email was sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Dein Verifizierungscode: {code}'
        msg['From'] = f'{settings.smtp_from_name} <{settings.smtp_from_email}>'
        msg['To'] = to_email
        
        # Plain text version
        text_content = f"""
Hallo,

dein Verifizierungscode für GetTheCode lautet:

{code}

Dieser Code ist 10 Minuten gültig.

Falls du keinen Code angefordert hast, kannst du diese E-Mail ignorieren.

Viele Grüße,
Dein GetTheCode by StefanAI Team

---
Impressum:
Stefan Müller | StefanAI
E-Mail: info@stefanai.de
Web: https://stefanai.de

Datenschutzerklärung: {settings.frontend_url}/datenschutz
"""
        
        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0d1117;
            color: #e6edf3;
            padding: 40px 20px;
            margin: 0;
        }}
        .container {{
            max-width: 480px;
            margin: 0 auto;
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 32px;
        }}
        p {{
            color: #e6edf3;
            line-height: 1.6;
        }}
        .logo {{
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: #39d353;
            margin-bottom: 24px;
        }}
        .logo-sub {{
            font-size: 14px;
            color: #b1bac4;
            font-weight: normal;
        }}
        .code-box {{
            background-color: #0d1117;
            border: 2px solid #39d353;
            border-radius: 8px;
            padding: 24px;
            text-align: center;
            margin: 24px 0;
        }}
        .code {{
            font-size: 36px;
            font-weight: bold;
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            color: #39d353;
            letter-spacing: 8px;
        }}
        .expiry {{
            color: #b1bac4;
            font-size: 14px;
            text-align: center;
            margin-top: 16px;
        }}
        .footer {{
            color: #b1bac4;
            font-size: 12px;
            text-align: center;
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #30363d;
        }}
        .footer a {{
            color: #58a6ff;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        .impressum {{
            margin-top: 16px;
            padding-top: 12px;
            border-top: 1px solid #21262d;
            font-size: 11px;
            color: #b1bac4;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            🎮 GetTheCode
            <div class="logo-sub">by StefanAI</div>
        </div>
        <p>Hallo,</p>
        <p>dein Verifizierungscode lautet:</p>
        <div class="code-box">
            <div class="code">{code}</div>
        </div>
        <p class="expiry">⏱️ Dieser Code ist 10 Minuten gültig.</p>
        <div class="footer">
            Falls du keinen Code angefordert hast, kannst du diese E-Mail ignorieren.<br><br>
            Dein GetTheCode by StefanAI Team
            <div class="impressum">
                <strong>Impressum:</strong> Stefan Müller | StefanAI<br>
                E-Mail: <a href="mailto:info@stefanai.de">info@stefanai.de</a> | 
                Web: <a href="https://stefanai.de" target="_blank">stefanai.de</a><br><br>
                <a href="{settings.frontend_url}/datenschutz" target="_blank">Datenschutzerklärung</a> | 
                <a href="{settings.frontend_url}/impressum" target="_blank">Impressum</a>
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        # Attach both versions
        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # Send email
        if settings.smtp_use_tls:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
        
        if settings.smtp_user and settings.smtp_password:
            server.login(settings.smtp_user, settings.smtp_password)
        
        server.sendmail(settings.smtp_from_email, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"Verification email sent to {to_email[:3]}***@***")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"Recipient refused: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending email: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        return False


def send_claim_confirmation_email(to_email: str, claim_id: int, claimed_code: str) -> bool:
    """
    Send a confirmation email after successful claim submission.
    
    Args:
        to_email: Recipient email address
        claim_id: The ID of the submitted claim
        claimed_code: The code the user claimed to have extracted
        
    Returns:
        True if email was sent successfully, False otherwise
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'GetTheCode: Deine Einreichung wurde bestaetigt'
        msg['From'] = f'{settings.smtp_from_name} <{settings.smtp_from_email}>'
        msg['To'] = to_email
        
        # Plain text version
        text_content = f"""
Hallo,

vielen Dank für deine Teilnahme bei GetTheCode!

Dein Gewinn-Anspruch wurde erfolgreich eingereicht.

Details:
- Claim-ID: #{claim_id}
- Eingereichter Code: {claimed_code}

Wie geht es weiter?
Ein Mitglied unseres Teams wird deinen Anspruch prüfen und den Chat-Verlauf analysieren. 
Bei erfolgreicher Verifizierung erhältst du per E-Mail einen Link zur Einlösung deines Gewinns.

Dies kann bis zu 48 Stunden dauern. Wir melden uns zeitnah bei dir!

Viele Grüße,
Dein GetTheCode by StefanAI Team

---
Impressum:
Stefan Müller | StefanAI
E-Mail: info@stefanai.de
Web: https://stefanai.de

Datenschutzerklärung: {settings.frontend_url}/datenschutz
"""
        
        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0d1117;
            color: #e6edf3;
            padding: 40px 20px;
            margin: 0;
        }}
        .container {{
            max-width: 520px;
            margin: 0 auto;
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 32px;
        }}
        p {{
            color: #e6edf3;
            line-height: 1.6;
        }}
        .logo {{
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: #39d353;
            margin-bottom: 24px;
        }}
        .logo-sub {{
            font-size: 14px;
            color: #b1bac4;
            font-weight: normal;
        }}
        .success-title {{
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            color: #39d353;
            margin-bottom: 24px;
        }}
        .details-box {{
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 16px;
            margin: 20px 0;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #21262d;
        }}
        .detail-row:last-child {{
            border-bottom: none;
        }}
        .detail-label {{
            color: #b1bac4;
        }}
        .detail-value {{
            color: #58d68d;
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
        }}
        .next-steps {{
            background-color: #1f6feb30;
            border: 1px solid #1f6feb70;
            border-radius: 8px;
            padding: 16px;
            margin: 20px 0;
        }}
        .next-steps-title {{
            color: #79c0ff;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .next-steps p {{
            margin: 8px 0;
            font-size: 14px;
            color: #e6edf3;
        }}
        .footer {{
            color: #b1bac4;
            font-size: 12px;
            text-align: center;
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #30363d;
        }}
        .footer a {{
            color: #58a6ff;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        .impressum {{
            margin-top: 16px;
            padding-top: 12px;
            border-top: 1px solid #21262d;
            font-size: 11px;
            color: #b1bac4;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            GetTheCode
            <div class="logo-sub">by StefanAI</div>
        </div>
        
        <div class="success-title">Dein Anspruch wurde eingereicht!</div>
        
        <p>Vielen Dank fuer deine Teilnahme bei GetTheCode!</p>
        
        <div class="details-box">
            <div class="detail-row">
                <span class="detail-label">Claim-ID:</span>
                <span class="detail-value">#{claim_id}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Eingereichter Code:</span>
                <span class="detail-value">{claimed_code}</span>
            </div>
        </div>
        
        <div class="next-steps">
            <div class="next-steps-title">Wie geht es weiter?</div>
            <p>Ein Mitglied unseres Teams wird deinen Anspruch pruefen und den Chat-Verlauf analysieren.</p>
            <p>Bei erfolgreicher Verifizierung erhaeltst du per E-Mail einen <strong>Link zur Einloesung</strong>.</p>
            <p>Dies kann bis zu 48 Stunden dauern. Wir melden uns zeitnah bei dir!</p>
        </div>
        
        <div class="footer">
            Dein GetTheCode by StefanAI Team
            <div class="impressum">
                <strong>Impressum:</strong> Stefan Müller | StefanAI<br>
                E-Mail: <a href="mailto:info@stefanai.de">info@stefanai.de</a> | 
                Web: <a href="https://stefanai.de" target="_blank">stefanai.de</a><br><br>
                <a href="{settings.frontend_url}/datenschutz" target="_blank">Datenschutzerklärung</a> | 
                <a href="{settings.frontend_url}/impressum" target="_blank">Impressum</a>
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        # Attach both versions
        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # Send email
        if settings.smtp_use_tls:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
        
        if settings.smtp_user and settings.smtp_password:
            server.login(settings.smtp_user, settings.smtp_password)
        
        server.sendmail(settings.smtp_from_email, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"Claim confirmation email sent to {to_email[:3]}***@***")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"Recipient refused: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending claim confirmation: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending claim confirmation: {e}")
        return False
