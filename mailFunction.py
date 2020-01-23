import email
import smtplib
import ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendMail(subject, body, receiver):
    message = MIMEMultipart()
    message["From"] = "projet19info7@gmail.com"
    message["To"] = receiver
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    filename = "test.log"

    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    message.attach(part)
    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login("projet19info7@gmail.com", "c!%NL6Fy6sZN")
        server.sendmail("projet19info7@gmail.com", receiver, text)

#sendMail("Test Mail", "Ceci est mon premier mail envoyé avec python", "arthur.quef@gmail.com")


def success():
    sendMail("Copie réussie ! Directory_Saver",
             "Les dossiers ont bien été enregistré, vous trouverez les log en pièce jointe.", "arthur.quef@gmail.com")


def failure():
    sendMail("Echec de la copie. Directory_Saver",
             "Il y a eu un problème lors de la copie. Cf les fichier de log en pièce jointe.", "arthur.quef@gmail.com")


success()
