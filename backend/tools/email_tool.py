import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(to_email: str, subject: str, body: str) -> str:
    """
    Simple email sending tool using SMTP. SMTP configuration is hardcoded in the tool.
    """
    from_email = "noreply@example.com"
    smtp_server = "smtp.example.com"
    smtp_port = 587
    smtp_user = "smtp_user"
    smtp_password = "smtp_password"

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
        return f"Email sent to {to_email}"
    except Exception as e:
        return f"[Email Error] {str(e)}"
