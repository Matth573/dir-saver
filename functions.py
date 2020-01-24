'''
    Module qui contient les fonction pour effectuer les copies selon les protocole
    Contient également le main.
'''
from ftplib import FTP, FTP_TLS, error_perm
from datetime import datetime
from stat import S_ISDIR
import shutil
import os
import sys
import logging
import paramiko

LOGGER = logging.getLogger('logger')
LOGGER.setLevel(logging.INFO)
FILEHANDLER = logging.FileHandler('test.log')
LOGGER.addHandler(FILEHANDLER)
FORMATTER = logging.Formatter('%(asctime)s  %(levelname)s: %(message)s')
FILEHANDLER.setFormatter(FORMATTER)

LOGGER.info(
    "Récupération des paramètres spécifiés dans le fichier de configuration")
ARGS = sys.argv
DIRPATH = ARGS[1]
METH = ARGS[2]
IP_URL_ADDRESS = ARGS[3]
LOGIN = ARGS[4]
PASSWORD = ARGS[5]
SAVEPATH = ARGS[6]
NREP = ARGS[7]
VERSIONNUMBER = ARGS[8]


def get_paths(directories_path):
    '''Fonction qui renvoie les chemins des différents répertoires à sauvegarder'''
    return directories_path.split(",")


def local_copy(src, dest):
    '''Fonction qui effectue la copie du dossier spécifié en locale dans le chemin de destination'''
    LOGGER.info("Copie du dossier")
    src = '/Users/matthieu/Documents/Telecom/Semestre 7/Scripting System/test'
    dest = '/Users/matthieu/Documents/Telecom/Semestre 7/Scripting System/test6'
    destination = shutil.copytree(src, dest)
    print(destination)


def copy_ftp(ftp, path):
    ''' Fonction qui copie le dossier indiqué par le chemin en paramètre en utilisant
        le protocole ftp
    '''
    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        if os.path.isfile(localpath):
            print("STOR", name, localpath)
            ftp.storbinary('STOR ' + name, open(localpath, 'rb'))
        elif os.path.isdir(localpath):
            print("MKD", name)

            ftp.mkd(name)

            print("CWD", name)
            ftp.cwd(name)
            copy_ftp(ftp, localpath)
            print("CWD", "..")
            ftp.cwd("..")


def copy_sftp(sftp, path):
    ''' Fonction qui copie le dossier indiqué par le chemin en paramètre en utilisant
        le protocole sftp
    '''
    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        if os.path.isfile(localpath):
            sftp.put(localpath, name)
        elif os.path.isdir(localpath):
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
    listdir = path.split('/')
    if listdir[0] == '':
        listdir.remove('')
    for directory in listdir:
        if not directory in ftp.nlst():
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


def version_handler(client):
    ''' Fonction qui vérifie s'il faut gérer le nombre de sauvegarde à garder
        sur le serveur et qui supprime des sauvegardes si besoin
    '''
    date_heure = datetime.now()
    date_heure = str(date_heure)
    if METH in ('FTPS', 'FTP'):
        if int(VERSIONNUMBER) > 0:
            if len(client.nlst()) >= int(VERSIONNUMBER):
                LOGGER.info(
                    "Nombre maximale de dossier sauvegardé atteint. Suppression de la plus vieille sauvegarde")
                LOGGER.info("Suppression du dossier %s", client.nlst()[0])
                remove_ftp_dir(client, SAVEPATH + "/" + client.nlst()[0])
        client.mkd(date_heure)
        client.cwd(date_heure)
    elif METH == "SFTP":
        if int(VERSIONNUMBER) > 0:
            if len(client.listdir()) >= int(VERSIONNUMBER):
                LOGGER.info(
                    "Nombre maximale de dossier sauvegardé atteint. Suppression de la plus vieille sauvegarde")
                LOGGER.info("Suppression du dossier %s", client.listdir()[0])
                remove_directory_sftp(client, client.listdir()[0])
        client.mkdir(date_heure)
        client.chdir(date_heure)


def main2():
    ''' Fonction main qui appelle les bonnes fonctions selon les paramètres renseigné
        dans le fichier de configuration.
    '''
    error = False
    try:
        if METH == "FTPS":
            client = FTP_TLS(IP_URL_ADDRESS, LOGIN, PASSWORD, SAVEPATH)
            go_to_directory_ftp(client, SAVEPATH)
        elif METH == "FTP":
            client = FTP(IP_URL_ADDRESS, LOGIN, PASSWORD, SAVEPATH)
            go_to_directory_ftp(client, SAVEPATH)
        elif METH == "SFTP":
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(IP_URL_ADDRESS, 22, LOGIN, PASSWORD)
            client = ssh.open_sftp()
            client.chdir("/sharedfolders/")
            go_to_directory_sftp(client, SAVEPATH)
    except error_perm as error:
        if str(error)[:3] == "550":
            LOGGER.warning("Le serveur requiert une connexion sur TLS")
            error = True
        else:
            LOGGER.error(error)
            error = True
    else:
        version_handler(client)
        if METH in ('FTPS', 'FTP'):
            for directory in DIRECTORY_LIST:
                LOGGER.info("Copie du dossier : %s", directory)
                name_directory = directory.split('/')[-1]
                client.mkd(name_directory)
                client.cwd(name_directory)
                copy_ftp(client, directory)
                client.cwd('..')
        elif METH == "SFTP":
            for directory in DIRECTORY_LIST:
                LOGGER.info("Copie du dossier : %s", directory)
                name_directory = directory.split('/')[-1]
                client.mkdir(name_directory)
                client.chdir(name_directory)
                copy_sftp(client, directory)
                client.chdir('..')
        client.close()


DIRECTORY_LIST = get_paths(DIRPATH)
main2()
