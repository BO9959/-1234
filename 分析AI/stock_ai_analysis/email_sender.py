# stock_ai_analysis/email_sender.py
import smtplib
from email.message import EmailMessage
import os
import mimetypes

def send_email(subject, body, to_emails, attachment_path=None,
               smtp_server="smtp.gmail.com", smtp_port=587,
               username="your_email@gmail.com", password="your_email_password"):
    """
    傳送 Email，若有附件則附加檔案
    """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = ", ".join(to_emails)
    msg.set_content(body)

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            file_data = f.read()
            mime_type, _ = mimetypes.guess_type(attachment_path)
            if mime_type is None:
                mime_type = "application/octet-stream"
            maintype, subtype = mime_type.split("/", 1)
            msg.add_attachment(file_data, maintype=maintype, subtype=subtype,
                               filename=os.path.basename(attachment_path))
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        print(f"Email 已成功寄送給 {to_emails}")
    except Exception as e:
        print("Email 傳送錯誤:", e)
