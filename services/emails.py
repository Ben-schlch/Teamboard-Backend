import os
import smtplib
import ssl


port_email = 465  # For SSL
password_email = os.getenv("gmailapppw")
gmail_adress = os.getenv("gmailprojadress")

# Create a secure SSL context
context = ssl.create_default_context()


async def send_email(adress: str, subject: str, message: str):
    with smtplib.SMTP_SSL("smtp.gmail.com", port_email, context=context) as server:
        server.login(gmail_adress, password_email)
        server.sendmail(gmail_adress, adress, f"Subject: {subject}\n\n{message}")
    print(f"{adress} {subject}")

async def send_reset_email(adress: str, token: str):
    with smtplib.SMTP_SSL("smtp.gmail.com", port_email, context=context) as server:
        server.login(gmail_adress, password_email)
        # Send link with adress and token
        server.sendmail(gmail_adress, adress, f"Subject: Password Reset\n\n"
                                              f"Hello,\n"
                                              f"you have requested a password reset. Please use the following link to reset your password:\n"
                                              f"{os.getenv('TEAMBOARD_URL', 'localhost:8000')}/reset/{adress}+{token}")
