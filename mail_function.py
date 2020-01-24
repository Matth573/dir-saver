''' Module qui contient les fonctions pour envoyer des mails à l'utilisateur'''

import smtplib
import ssl
import configparser
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def config_init():
    config = configparser.RawConfigParser()
    config.read('config.ini')
    return config


def send_mail(subject, body):
    ''' Fonction qui envoie un mail au destinataire avec l'objet et le corps en paramètre
    '''
    config = config_init()
    FROM_ADDRESS = config.get('mail', 'smtp_host_email_address')
    TO_ADDRESS = config.get('mail', 'send_to')
    SMTP_URL = config.get('mail', 'smtp_host')
    SMTP_PORT = config.get('mail', 'smtp_port')
    PASSWORD = config.get('mail', 'smtp_password')
    LOG_ON = config.get('directories', 'log_attached')

    message = MIMEMultipart()
    message["From"] = FROM_ADDRESS
    message["To"] = TO_ADDRESS
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
    with smtplib.SMTP_SSL(SMTP_URL, SMTP_PORT, context=context) as server:
        server.login(FROM_ADDRESS, PASSWORD)
        server.sendmail(FROM_ADDRESS, TO_ADDRESS, text)

#sendMail("Test Mail", "Ceci est mon premier mail envoyé avec python", "arthur.quef@gmail.com")


def success():
    ''' Fonction qui envoie un mail disant que la copie des dossiers s'est bien passé'''
    send_mail("Copie réussie ! Directory_Saver",
              "Les dossiers ont bien été enregistré, vous trouverez les log en pièce jointe.")


def failure():
    ''' Fonction qui envoie un mail disant qu'il y a eu un problème lors de la copie'''
    send_mail("Echec de la copie. Directory_Saver",
              "Il y a eu un problème lors de la copie. Cf les fichier de log en pièce jointe.",
              "arthur.quef@gmail.com")


success()
