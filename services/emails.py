import smtplib, ssl
import os

port_email = 465  # For SSL
password_email = os.getenv("emailpw")
gmail_adress = os.getenv("email")

# Create a secure SSL context
context = ssl.create_default_context()


def send_email(adress: str, subject: str, message: str):
    with smtplib.SMTP_SSL("smtp.gmail.com", port_email, context=context) as server:
        server.login(gmail_adress, password_email)
        server.sendmail(gmail_adress, adress, f"Subject: {subject}\n\n{message}")
    print(f"{adress} {subject} {message}")
