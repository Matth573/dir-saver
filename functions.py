'''
    Module qui contient les fonction pour effectuer les copies selon les protocole
    Contient également le main.
'''
from ftplib import FTP, FTP_TLS, error_perm
from datetime import datetime
from stat import S_ISDIR
import shutil
import os
import smtplib
import socket
import logging
import configparser
import mail_function as mail
import paramiko
import verif_config


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(levelname)s: %(message)s',
                    datefmt='%d-%m %H:%M',
                    filename='dir-saver.log',
                    filemode='w')
LOGGER = logging.getLogger('logger')

LOGGER.info(
    "Récupération des paramètres spécifiés dans le fichier de configuration")


CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')
DIRECTORIES_TO_SAVE = CONFIG.get('directories', 'directories_to_save')
WITH_FTP = CONFIG.getboolean('save_method', 'with_ftp')
WITH_FTPS = CONFIG.getboolean('save_method', 'with_ftps')
WITH_SFTP = CONFIG.getboolean('save_method', 'WITH_SFTP')
WITH_LOCAL_SAVE = CONFIG.getboolean('save_method', 'with_local_save')
IP_URL_ADDRESS = CONFIG.get('connection_parameters', 'ip_url_address')
LOGIN = CONFIG.get('connection_parameters', 'login')
PASSWORD = CONFIG.get('connection_parameters', 'password')
BACKUP_DIRECTORY = CONFIG.get('directories', 'backup_directory')
VERSION_CONTROL = CONFIG.getboolean('version_handler', 'version_control')
VERSION_NUMBER = CONFIG.get('version_handler', 'version_number')
VERSION_FORMAT = CONFIG.get('version_handler', 'format')
MAIL_ON = CONFIG.getboolean('mail', 'get_mail')
nb_file_save = 0
size_save = 0
directories_saved = 0
name_directory = None
directory_removed = None


def get_paths(directories_path):
    '''Fonction qui renvoie les chemins des différents répertoires à sauvegarder'''
    return directories_path.split(",")


def local_copy(src, dest):
    '''Fonction qui effectue la copie du dossier spécifié en locale dans le chemin de destination'''
    LOGGER.info("Copie du dossier %s", src.split('/')[-1])
    shutil.copytree(src, dest)


def copy_ftp(ftp, path):
    ''' Fonction qui copie le dossier indiqué par le chemin en paramètre en utilisant
        le protocole ftp
    '''
    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        if os.path.isfile(localpath):
            LOGGER.info("Copie du fichier %s", localpath)
            ftp.storbinary('STOR ' + name, open(localpath, 'rb'))
            global nb_file_save
            nb_file_save += 1
        elif os.path.isdir(localpath):
            LOGGER.info("Copie du dossier %s", localpath)
            ftp.mkd(name)
            ftp.cwd(name)
            copy_ftp(ftp, localpath)
            ftp.cwd("..")


def copy_sftp(sftp, path):
    ''' Fonction qui copie le dossier indiqué par le chemin en paramètre en utilisant
        le protocole sftp
    '''
    global nb_file_save
    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        if os.path.isfile(localpath):
            sftp.put(localpath, name)
            LOGGER.info("Copie du fichier %s", localpath)
            nb_file_save += 1
        elif os.path.isdir(localpath):
            LOGGER.info("Copie du dossier %s", localpath)
            sftp.mkdir(name)
            sftp.chdir(name)
            copy_sftp(sftp, localpath)
            sftp.chdir('..')


def remove_ftp_dir(ftp, path):
    ''' Fonction qui supprime un dossier du serveur en utilisant le protocole ftp'''
    for (name, properties) in ftp.mlsd(path=path):
        if name in ['.', '..']:
            continue
        if properties['type'] == 'file':
            ftp.delete(f"{path}/{name}")
        elif properties['type'] == 'dir':
            remove_ftp_dir(ftp, f"{path}/{name}")
    ftp.rmd(path)


def is_directory(sftp, path):
    ''' Fonction qui vérifie si le dossier spécifié est un dossier en utilisant
        le protocole sftp
    '''
    try:
        return S_ISDIR(sftp.stat(path).st_mode)
    except IOError:
        return False


def remove_directory_sftp(sftp, path):
    ''' Fonction qui supprime un dossier en utilisant le protocole sftp'''
    files = sftp.listdir(path=path)
    for file in files:
        filepath = os.path.join(path, file)
        if is_directory(sftp, filepath):
            remove_directory_sftp(sftp, filepath)
        else:
            sftp.remove(filepath)
    sftp.rmdir(path)


def go_to_directory_ftp(ftp, path):
    ''' Fonction qui permet de se déplacer dans le dossier voulu sur le serveur.
        Si le chemin n'existe pas, la fonction créé les répertoires manquants.
        Utilise le protocole ftp.
    '''
    LOGGER.info("Déplacement jusqu'au dossier : %s", path)
    listdir = path.split('/')
    if listdir[0] == '':
        listdir.remove('')
    for directory in listdir:
        if not directory in ftp.nlst():
            LOGGER.info(
                "Le dossier %s n'existe pas, création du dossier", directory)
            ftp.mkd(directory)
        ftp.cwd(directory)


def go_to_directory_sftp(sftp, path):
    ''' Fonction qui permet de se déplacer dans le dossier voulu sur le serveur.
        Si le chemin n'existe pas, la fonction créé les répertoires manquants.
        Utilise le protocole ftp.
    '''
    LOGGER.info("Déplacement jusqu'au dossier : %s", path)
    listdir = path.split('/')
    if listdir[0] == '':
        listdir.remove('')
    for directory in listdir:
        if not directory in sftp.listdir():
            LOGGER.info(
                "Le dossier %s n'existe pas, création du dossier", directory)
            sftp.mkdir(directory)
        sftp.chdir(directory)


def go_to_directory_local(path):
    LOGGER.info("Déplacement jusqu'au dossier : %s", path)
    os.system('cd ' + path)
    print(os.popen('pwd').read())
    #listdir = path.split('/')
    # if listdir[0] == '':
    #    listdir.remove('')
    # for directory in listdir:
    #    print(os.popen('ls -a').read().split('\n'))
    #    if not directory in os.popen('ls -a').read().split('\n'):
    #        LOGGER.info(
    #            "Le dossier %s n'existe pas, création du dossier", directory)
    #        os.system('mkdir ' + directory)
    #    os.system('cd ' + directory)


def get_last_number_sftp(client):
    ''' Fonction qui résupère le dernier nombre utilisé pour faire une sauvegarde avec sftp'''
    if len(client.listdir()) != 0:
        return max([int(i) for i in client.listdir()])
    else:
        return 0


def get_last_number_ftp(client):
    ''' Fonction qui résupère le dernier nombre utilisé pour faire une sauvegarde avec ftp'''
    if len(client.nlst()) != 0:
        return max([int(i) for i in client.nlst()])
    else:
        return 0


def get_last_number_local(path):
    list = os.popen('ls ' + BACKUP_DIRECTORY.replace(' ','\ ')).read().split('\n')
    if len(list) > 0:
        return max([int(i) for i in list])
    else:
        return 0


def version_handler(client):
    ''' Fonction qui vérifie s'il faut gérer le nombre de sauvegarde à garder
        sur le serveur et qui supprime des sauvegardes si besoin
    '''
    global directory_removed
    global name_directory
    if VERSION_FORMAT == "date":
        name_directory = str(datetime.now())
    elif VERSION_FORMAT == "number":
        if WITH_FTP or WITH_FTPS:
            name_directory = str(get_last_number_ftp(client) + 1)
        elif WITH_SFTP:
            name_directory = str(get_last_number_sftp(client) + 1)
        elif WITH_LOCAL_SAVE:
            name_directory = str(get_last_number_local() + 1)
    if WITH_FTP or WITH_FTPS:
        if VERSION_CONTROL:
            while len(client.nlst()) >= int(VERSION_NUMBER):
                LOGGER.info(
                    "Nombre maximale de dossier sauvegardé atteint. Suppression de la plus vieille sauvegarde")
                if VERSION_FORMAT == "date":
                    LOGGER.info("Suppression du dossier %s", client.nlst()[0])
                    directory_removed = client.nlst()[0]
                    remove_ftp_dir(client, BACKUP_DIRECTORY +
                                   "/" + client.nlst()[0])
                elif VERSION_FORMAT == "number":
                    directory_removed = min([int(i) for i in client.nlst()])
                    LOGGER.info("Suppression du dossier %s", directory_removed)
                    remove_ftp_dir(client, BACKUP_DIRECTORY +
                                   "/" + str(directory_removed))
        LOGGER.info("Création du dossier de sauvegarde : %s", name_directory)
        client.mkd(name_directory)
        client.cwd(name_directory)
    elif WITH_SFTP:
        if VERSION_CONTROL:
            while len(client.listdir()) >= int(VERSION_NUMBER):
                LOGGER.info(
                    "Nombre maximale de dossier sauvegardé atteint. Suppression de la plus vieille sauvegarde")
                if VERSION_FORMAT == "date":
                    LOGGER.info("Suppression du dossier %s",
                                client.listdir()[0])
                    directory_removed = client.listdir()[0]
                    remove_directory_sftp(client, client.listdir()[0])
                elif VERSION_FORMAT == "number":
                    directory_removed = min([int(i) for i in client.listdir()])
                    LOGGER.info("Suppression du dossier %s", directory_removed)
                    remove_directory_sftp(client, str(directory_removed))
        LOGGER.info("Création du dossier de sauvegarde : %s", name_directory)
        client.mkdir(name_directory)
        client.chdir(name_directory)
    elif WITH_LOCAL_SAVE:
        if VERSION_CONTROL:
            while len(os.popen('ls ' + BACKUP_DIRECTORY.replace(' ','\ ')).read()) >= int(VERSION_NUMBER):
                LOGGER.info(
                    "Nombre maximale de dossier sauvegardé atteint. Suppression de la plus vieille sauvegarde")
                if VERSION_FORMAT == "date":
                    directory_removed = os.popen(
                        'ls ' + BACKUP_DIRECTORY.replace(' ','\ ')).read().split('\n')[0]
                    LOGGER.info("Suppression du dossier %s",
                                directory_removed)
                    os.system('rm -r ' + directory_removed)
                elif VERSION_FORMAT == "number":
                    directory_removed = get_last_number_local()
                    LOGGER.info("Suppression du dossier %s", directory_removed)
                    os.system('rm -r ' + directory_removed)
        LOGGER.info("Création du dossier de sauvegarde : %s", name_directory)
        os.system("mkdir " + BACKUP_DIRECTORY.replace(' ','\ ') + '/' + name_directory.replace(' ','\ '))


def main():
    ''' Fonction main qui appelle les bonnes fonctions selon les paramètres renseigné
        dans le fichier de configuration.
    '''
    global directory_removed
    try:
        if WITH_FTPS:
            LOGGER.info("Utilisation du protocole FTPS")
            client = FTP_TLS(IP_URL_ADDRESS, LOGIN, PASSWORD, BACKUP_DIRECTORY)
            go_to_directory_ftp(client, BACKUP_DIRECTORY)
        elif WITH_FTP:
            LOGGER.info("Utilisation du protocole FTP")
            client = FTP(IP_URL_ADDRESS, LOGIN, PASSWORD, BACKUP_DIRECTORY)
            go_to_directory_ftp(client, BACKUP_DIRECTORY)
        elif WITH_SFTP:
            LOGGER.info("Utilisation du protocole SFTP")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(IP_URL_ADDRESS, 22, LOGIN, PASSWORD)
            client = ssh.open_sftp()
            client.chdir("/sharedfolders/")
            go_to_directory_sftp(client, BACKUP_DIRECTORY)
        elif WITH_LOCAL_SAVE:
            client = None
    except PermissionError as error:
        LOGGER.warning(
            "Impossible d'écrire dans le seveur. Vérifiez le chemin spécifié pour la sauvegarde et les droits de l'utilisateur renseigné.")
    except paramiko.ssh_exception.AuthenticationException as error:
        LOGGER.warning(
            "Erreur lors de l'authentification au serveur. Vérifiez identifiants et mot de passe.")
    except TimeoutError as error:
        LOGGER.warning(
            "Impossible de joindre le serveur, Vérifiez l'adresse du serveur.")
    except ConnectionRefusedError as error:
        LOGGER.warning("Le serveur a refuser la connection.")
    except error_perm as error:
        if str(error)[:3] == "550":
            LOGGER.warning(
                "Permission refusé, vérifier que vous avez les bons droits sur le serveur")
        else:
            LOGGER.error(error)
    else:
        try:
            version_handler(client)
        except ValueError as error:
            LOGGER.warning(
                "La nomenclature des dossiers à changé, vous devez retourner à l'ancienne version ou supprimer les sauvegardes existantes.")
        else:
            if WITH_FTP or WITH_FTPS:
                for directory in DIRECTORY_LIST:
                    LOGGER.info("Copie du dossier : %s", directory)
                    name_directory_backup = directory.split('/')[-1]
                    client.mkd(name_directory_backup)
                    client.cwd(name_directory_backup)
                    try:
                        copy_ftp(client, directory)
                    except FileNotFoundError as error:
                        LOGGER.warning(
                            "Un dossier à enregistrer n'existe pas. Vérifiez le chemin fourni")
                    else:
                        client.cwd('..')
                        global size_save
                        size_save += int(os.popen("du -sk " +
                                                  directory.replace(' ', '\ ') +
                                                  " | awk '{print $1}'").read())
            elif WITH_SFTP:
                for directory in DIRECTORY_LIST:
                    LOGGER.info("Copie du dossier : %s", directory)
                    name_directory_backup = directory.split('/')[-1]
                    client.mkdir(name_directory_backup)
                    client.chdir(name_directory_backup)
                    try:
                        copy_sftp(client, directory)
                    except FileNotFoundError as error:
                        LOGGER.warning(
                            "Un dossier à enregistrer n'existe pas. Vérifiez le chemin fourni")
                    else:
                        client.chdir('..')
                        size_save += int(os.popen("du -sk " +
                                                  directory.replace(' ', '\ ') +
                                                  " | awk '{print $1}'").read())
            elif WITH_LOCAL_SAVE:
                for directory in DIRECTORY_LIST:
                    LOGGER.info("Copie du dossier : %s", directory)
                    name_directory_backup = directory.split('/')[-1]
                    name_directory_backup = BACKUP_DIRECTORY + '/' + name_directory_backup
                    local_copy(directory,name_directory_backup)
            if not WITH_LOCAL_SAVE:
                client.close()


DIRECTORY_LIST = get_paths(DIRECTORIES_TO_SAVE)
config_ok = verif_config.main()
if config_ok == "ok":
    main()
    with open("dir-saver.log", "r") as log:
        text = "".join(log.readlines())
        if text.find("WARNING") != -1 or text.find("ERROR") != -1:
            error = True
        else:
            error = False
    if not error:
        LOGGER.info("Copie réussie !")
        LOGGER.info("Nombre de fichiers sauvegardés : %s", nb_file_save)
        LOGGER.info("Volume sauvegardé : %s Ko", size_save)
        if directory_removed != None:
            LOGGER.info(
                "La précédente sauvegarde contenue dans le dossier '%s' a été supprimé",
                directory_removed)
        LOGGER.info("Nom du dossier de sauvegarde : %s", name_directory)
        if MAIL_ON:
            try:
                mail.success()
            except socket.gaierror as error:
                LOGGER.warning("Impossible de se connecter au serveur SMTP")
            except TimeoutError as error:
                LOGGER.warning(
                    "Pas de reponse du serveur SMTP, vérifiez l' adresse et le port.")
            except smtplib.SMTPAuthenticationError as error:
                LOGGER.warning(
                    "Erreur lors de l'authentification au serveur SMTP, vérifiez mot de passe et adresse mail")
    else:
        if MAIL_ON:
            try:
                mail.failure()
            except socket.gaierror as error:
                LOGGER.warning("Impossible de se connecter au serveur SMTP")
            except TimeoutError as error:
                LOGGER.warning(
                    "Pas de reponse du serveur SMTP, vérifiez l' adresse et le port.")
            except smtplib.SMTPAuthenticationError as error:
                LOGGER.warning(
                    "Erreur lors de l'authentification au serveur SMTP, vérifiez mot de passe et adresse mail")
else:
    LOGGER.warning(config_ok)
    print(config_ok)
