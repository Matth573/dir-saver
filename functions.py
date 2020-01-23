from ftplib import FTP, FTP_TLS, error_perm
from os import walk
import shutil
import os
import sys
import logging
import paramiko
import pdb
from datetime import datetime
from stat import S_ISDIR

LOGGER = logging.getLogger('logger')
LOGGER.setLevel(logging.INFO)
FILEHANDLER = logging.FileHandler('test.log')
LOGGER.addHandler(FILEHANDLER)
FORMATTER = logging.Formatter('%(asctime)s  %(levelname)s: %(message)s')
FILEHANDLER.setFormatter(FORMATTER)

# Récupération des variables définies dans le fichier de conf:
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


def remove_directory(sftp, path):
    ''' Fonction qui supprime un dossier en utilisant le protocole sftp'''
    files = sftp.listdir(path=path)

    for file in files:
        filepath = os.path.join(path, file)
        if is_directory(sftp, filepath):
            remove_directory(sftp, filepath)
        else:
            sftp.remove(filepath)

    sftp.rmdir(path)


def go_to_directory(ftp, path):
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


def go_to_directory_ssh(ssh, path):
    ''' Fonction qui permet de se déplacer dans le dossier voulu sur le serveur.
        Si le chemin n'existe pas, la fonction créé les répertoires manquants.
        Utilise le protocole ftp.
    '''
    listdir = path.split('/')
    if listdir[0] == '':
        listdir.remove('')
    for directory in listdir:
        if not directory in ssh.listdir():
            ssh.mkdir(directory)
        ssh.chdir(directory)


def main():
    ''' Fonction main qui appelle les bonnes fonctions selon les paramètres renseigné
        dans le fichier de configuration.
    '''

    if METH == "FTPS":
        LOGGER.info("Copie en utilisant le protocole FTPS")
        try:
            ftp = FTP(IP_URL_ADDRESS, LOGIN, PASSWORD, SAVEPATH)
        except error_perm as error:
            if str(error)[:3] == "550":
                print("Le serveur requiert une connexion sur TLS")
            else:
                print(error)
        else:
            go_to_directory(ftp, SAVEPATH)
            if len(ftp.nlst()) >= int(VERSIONNUMBER):
                remove_ftp_dir(ftp, SAVEPATH + "/" + ftp.nlst()[0])
            date_heure = datetime.now()
            ftp.mkd(str(date_heure))
            ftp.cwd(str(date_heure))
            for directory in directoryList:
                LOGGER.info("Copie du dossier : %s", directory)
                name_directory = directory.split('/')[-1]
                ftp.mkd(name_directory)
                ftp.cwd(name_directory)
                copy_ftp(ftp, directory)
                ftp.cwd('..')
            ftp.close()

    if METH == "FTP":
        LOGGER.info("Copie en utilisant le protocole FTP")
        try:
            ftp = FTP(IP_URL_ADDRESS, LOGIN, PASSWORD, SAVEPATH)
        except error_perm as error:
            if str(error)[:3] == "550":
                print("Le serveur requiert une connexion sur TLS")
            else:
                print(error)
        else:
            go_to_directory(ftp, SAVEPATH)
            if len(ftp.nlst()) >= int(VERSIONNUMBER):
                remove_ftp_dir(ftp, SAVEPATH + "/" + ftp.nlst()[0])
            date_heure = datetime.now()
            ftp.mkd(str(date_heure))
            ftp.cwd(str(date_heure))
            for directory in directoryList:
                LOGGER.info("Copie du dossier : %s", directory)
                name_directory = directory.split('/')[-1]
                ftp.mkd(name_directory)
                ftp.cwd(name_directory)
                copy_ftp(ftp, directory)
                ftp.cwd('..')
            ftp.close()
    if METH == "SFTP":
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(IP_URL_ADDRESS, 22, LOGIN, PASSWORD)
        sftp = ssh.open_sftp()
        sftp.chdir("/sharedfolders/")
        go_to_directory_ssh(sftp, SAVEPATH)
        if len(sftp.listdir()) >= int(VERSIONNUMBER):
            remove_directory(sftp, sftp.listdir()[0])
        date_heure = datetime.now()
        sftp.mkdir(str(date_heure))
        sftp.chdir(str(date_heure))
        for directory in directoryList:
            LOGGER.info("Copie du dossier : " + directory)
            name_directory = directory.split('/')[-1]
            sftp.mkdir(name_directory)
            sftp.chdir(name_directory)
            copy_sftp(sftp, directory)
            sftp.chdir('..')
        ssh.close()


directoryList = get_paths(DIRPATH)
main()
