''' Module qui contient les fonctions pour envoyer des mails à l'utilisateur'''

import smtplib
import ssl
import configparser
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def config_init():
    ''' Fonction qui récupère les paramètre du fichier de configuration'''
    config = configparser.RawConfigParser()
    config.read('config.ini')
    return config


def send_mail(subject, body):
    ''' Fonction qui envoie un mail au destinataire avec l'objet et le corps en paramètre
    '''
    config = config_init()
    from_address = config.get('mail', 'smtp_host_email_address')
    to_address = config.get('mail', 'send_to')
    smtp_url = config.get('mail', 'smtp_host')
    smtp_port = config.get('mail', 'smtp_port')
    password = config.get('mail', 'smtp_password')
    log_on = config.get('mail', 'log_attached')

    message = MIMEMultipart()
    message["From"] = from_address
    message["To"] = to_address
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
    with smtplib.SMTP_SSL(smtp_url, smtp_port, context=context) as server:
        server.login(from_address, password)
        server.sendmail(from_address, to_address, text)


def success():
    ''' Fonction qui envoie un mail disant que la copie des dossiers s'est bien passé'''
    send_mail("Copie réussie ! Directory_Saver",
              "Les dossiers ont bien été enregistré, vous trouverez les log en pièce jointe.")


def failure():
    ''' Fonction qui envoie un mail disant qu'il y a eu un problème lors de la copie'''
    send_mail("Echec de la copie. Directory_Saver",
              "Il y a eu un problème lors de la copie. Cf les fichier de log en pièce jointe.")


#success()
