import os
import smtplib
import ssl


port_email = 465  # For SSL
password_email = os.getenv("gmailapppw")
gmail_adress = os.getenv("gmailprojadress")

# Create a secure SSL context
context = ssl.create_default_context()


def send_email(adress: str, subject: str, message: str):
    with smtplib.SMTP_SSL("smtp.gmail.com", port_email, context=context) as server:
        server.login(gmail_adress, password_email)
        server.sendmail(gmail_adress, adress, f"Subject: {subject}\n\n{message}")
    print(f"{adress} {subject} {message}")


def manipulate_gmail_adress(adress: str):
    if "@gmail" in adress:
        first, second = adress.split("@")
        first = first.replace(".", "")
        adress = f"{first}@{second}"
    return adress


def request_join_email(email, sender_email, teamboard_name):
    message = f"Hello!\n\n{sender_email} wants to add you to the teamboard {teamboard_name}.\n\n" \
              f"Please register using this link:{os.getenv('TEAMBOARD_URL')}"
    send_email(email, "Teamboard Invitation", message)