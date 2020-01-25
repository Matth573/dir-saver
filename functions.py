'''
    Module qui contient les fonction pour effectuer les copies selon les protocole
    Contient également le main.
'''
from ftplib import FTP, FTP_TLS, error_perm
from datetime import datetime
from stat import S_ISDIR
import shutil
import os
import logging
import configparser
import mail_function
import paramiko


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
WITH_FTP = CONFIG.get('save_method', 'with_ftp')
WITH_FTPS = CONFIG.get('save_method', 'with_ftps')
WITH_SFTP = CONFIG.get('save_method', 'WITH_SFTP')
WITH_LOCAL_SAVE = CONFIG.get('save_method', 'with_local_save')
IP_URL_ADDRESS = CONFIG.get('connection_parameters', 'ip_url_address')
LOGIN = CONFIG.get('connection_parameters', 'login')
PASSWORD = CONFIG.get('connection_parameters', 'password')
BACKUP_DIRECTORY = CONFIG.get('directories', 'backup_directory')
VERSION_CONTROL = CONFIG.get('version_handler', 'version_control')
VERSION_NUMBER = CONFIG.get('version_handler', 'version_number')
VERSION_FORMAT = CONFIG.get('version_handler', 'format')
MAIL_ON = CONFIG.get('mail', 'get_mail')
nb_file_save = 0
size_save = 0
directories_saved = 0
name_directory = None
directory_removed = None
error = False


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


def version_handler(client):
    ''' Fonction qui vérifie s'il faut gérer le nombre de sauvegarde à garder
        sur le serveur et qui supprime des sauvegardes si besoin
    '''
    if VERSION_FORMAT == "date":
        name_directory = str(datetime.now())
    elif VERSION_FORMAT == "number":
        if WITH_FTP or WITH_FTPS:
            name_directory = str(get_last_number_ftp(client) + 1)
        elif WITH_SFTP:
            name_directory = str(get_last_number_sftp(client) + 1)
    if WITH_FTP or WITH_FTPS:
        if VERSION_CONTROL:
            if len(client.nlst()) >= int(VERSION_NUMBER):
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
            if len(client.listdir()) >= int(VERSION_NUMBER):
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


def main():
    ''' Fonction main qui appelle les bonnes fonctions selon les paramètres renseigné
        dans le fichier de configuration.
    '''
    error = False
    try:
        if WITH_FTPS:
            client = FTP_TLS(IP_URL_ADDRESS, LOGIN, PASSWORD, BACKUP_DIRECTORY)
            go_to_directory_ftp(client, BACKUP_DIRECTORY)
        elif WITH_FTP:
            client = FTP(IP_URL_ADDRESS, LOGIN, PASSWORD, BACKUP_DIRECTORY)
            go_to_directory_ftp(client, BACKUP_DIRECTORY)
        elif WITH_SFTP:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(IP_URL_ADDRESS, 22, LOGIN, PASSWORD)
            client = ssh.open_sftp()
            client.chdir("/sharedfolders/")
            go_to_directory_sftp(client, BACKUP_DIRECTORY)
    except error_perm as error:
        if str(error)[:3] == "550":
            LOGGER.warning("Le serveur requiert une connexion sur TLS")
            error = True
        else:
            LOGGER.error(error)
            error = True
    else:
        version_handler(client)
        if WITH_FTP or WITH_FTPS:
            for directory in DIRECTORY_LIST:
                LOGGER.info("Copie du dossier : %s", directory)
                name_directory = directory.split('/')[-1]
                client.mkd(name_directory)
                client.cwd(name_directory)
                copy_ftp(client, directory)
                client.cwd('..')
                global size_save
                size_save += int(os.popen("du -sk " +
                                           directory.replace(' ','\ ') + " | awk '{print $1}'").read())
        elif WITH_SFTP:
            for directory in DIRECTORY_LIST:
                LOGGER.info("Copie du dossier : %s", directory)
                name_directory = directory.split('/')[-1]
                client.mkdir(name_directory)
                client.chdir(name_directory)
                copy_sftp(client, directory)
                client.chdir('..')
                size_save += int(
                    os.system("du -s %s | awk '{print $1}'", directory))
        client.close()


DIRECTORY_LIST = get_paths(DIRECTORIES_TO_SAVE)
main()
if not error:
    LOGGER.info("Copie réussie !")
    LOGGER.info("Nombre de fichiers sauvegardés : %s", nb_file_save)
    LOGGER.info("Volume sauvegardé : %s Ko", size_save)
