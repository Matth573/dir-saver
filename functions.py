import os
import sys
import logging
import paramiko
import pdb
from datetime import datetime
from stat import S_ISDIR

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
fileHandler = logging.FileHandler('test.log')
logger.addHandler(fileHandler)
formatter = logging.Formatter('%(asctime)s  %(levelname)s: %(message)s')
fileHandler.setFormatter(formatter)

#Récupération des variables définies dans le fichier de conf:
logger.info("Récupération des paramètres spécifiés dans le fichier de configuration")
args=sys.argv
DIRPATH=args[1]
METH=args[2]
IP_URL_ADDRESS=args[3]
LOGIN=args[4]
PASSWORD=args[5]
SAVEPATH=args[6]
NREP=args[7]
VERSIONNUMBER=args[8]


def getpaths(directoriesPath):
    return directoriesPath.split(",")

from os import walk
import shutil
def localCopy(src,dest):
    logger.info("Copie du dossier")
    src='/Users/matthieu/Documents/Telecom/Semestre 7/Scripting System/test'
    dest='/Users/matthieu/Documents/Telecom/Semestre 7/Scripting System/test6'
    destination = shutil.copytree(src,dest)
    print(destination)

from ftplib import FTP,FTP_TLS,error_perm

import os
def copyftp(ftp,path):
    for name in os.listdir(path):
        localpath = os.path.join(path,name)
        if os.path.isfile(localpath):
            print("STOR", name, localpath)
            ftp.storbinary('STOR ' + name, open(localpath,'rb'))
        elif os.path.isdir(localpath):
            print("MKD", name)

            ftp.mkd(name)

            print("CWD", name)
            ftp.cwd(name)
            copyftp(ftp, localpath)
            print("CWD", "..")
            ftp.cwd("..")

def copyssh(ssh,path):
    for name in os.listdir(path):
        localpath = os.path.join(path,name)
        if os.path.isfile(localpath):
            ssh.put(localpath, name)
        elif os.path.isdir(localpath):
            ssh.mkdir(name)
            ssh.chdir(name)
            copyssh(ssh, localpath)
            ssh.chdir('..')

def remove_ftp_dir(ftp, path):
    for (name, properties) in ftp.mlsd(path=path):
        if name in ['.', '..']:
            continue
        elif properties['type'] == 'file':
            ftp.delete(f"{path}/{name}")
        elif properties['type'] == 'dir':
            remove_ftp_dir(ftp, f"{path}/{name}")
    ftp.rmd(path)

def isdir(sftp, path):
    try:
        return S_ISDIR(sftp.stat(path).st_mode)
    except IOError:
        return False

def rm(sftp, path):
    files = sftp.listdir(path=path)

    for f in files:
        filepath = os.path.join(path, f)
        if isdir(sftp,filepath):
            rm(sftp,filepath)
        else:
            sftp.remove(filepath)

    sftp.rmdir(path)


def goToDirectory(ftp,path):
    listdir=path.split('/')
    if listdir[0]=='':
        listdir.remove('')
    for directory in listdir:
        if not directory in ftp.nlst():
            ftp.mkd(directory)
        ftp.cwd(directory)

def goToDirectorySSH(ssh,path):
    listdir=path.split('/')
    if listdir[0]=='':
        listdir.remove('')
    for directory in listdir:
        if not directory in ssh.listdir():
            ssh.mkdir(directory)
        ssh.chdir(directory)


def main():

    if METH == "FTPS" :
        logger.info("Copie en utilisant le protocole FTPS")
        try:
            ftp = FTP(IP_URL_ADDRESS,LOGIN,PASSWORD,SAVEPATH)
        except error_perm as e:
            if str(e)[:3] == "550":
                print("Le serveur requiert une connexion sur TLS")
            else:
                print(e)
        else:
            goToDirectory(ftp,SAVEPATH)
            if len(ftp.nlst()) >= int(VERSIONNUMBER):
                remove_ftp_dir(ftp, SAVEPATH + "/"+ftp.nlst()[0])
            d=datetime.now()
            ftp.mkd(str(d))
            ftp.cwd(str(d))
            for directory in directoryList:
                logger.info("Copie du dossier : "+directory)
                nameDirectory = directory.split('/')[-1]
                ftp.mkd(nameDirectory)
                ftp.cwd(nameDirectory)
                copyftp(ftp,directory)
                ftp.cwd('..') 
            ftp.close()

    if METH == "FTP" : 
        logger.info("Copie en utilisant le protocole FTP")
        try:
            ftp = FTP(IP_URL_ADDRESS,LOGIN,PASSWORD,SAVEPATH)
        except error_perm as e:
            if str(e)[:3] == "550":
                print("Le serveur requiert une connexion sur TLS")
            else:
                print(e)
        else:
            goToDirectory(ftp,SAVEPATH)
            if len(ftp.nlst()) >= int(VERSIONNUMBER):
                remove_ftp_dir(ftp, SAVEPATH + "/"+ftp.nlst()[0])
            d=datetime.now()
            ftp.mkd(str(d))
            ftp.cwd(str(d))
            for directory in directoryList:
                logger.info("Copie du dossier : "+directory)
                nameDirectory = directory.split('/')[-1]
                ftp.mkd(nameDirectory)
                ftp.cwd(nameDirectory)
                copyftp(ftp,directory)
                ftp.cwd('..') 
            ftp.close()
    if METH == "SFTP":
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(IP_URL_ADDRESS,22,LOGIN,PASSWORD)
        sftp = ssh.open_sftp()
        sftp.chdir("/sharedfolders/")
        goToDirectorySSH(sftp,SAVEPATH)
        if len(sftp.listdir()) >= int(VERSIONNUMBER):
            rm(sftp,sftp.listdir()[0])
        d=datetime.now()
        sftp.mkdir(str(d))
        sftp.chdir(str(d))
        for directory in directoryList:
            logger.info("Copie du dossier : "+directory)
            nameDirectory = directory.split('/')[-1]
            sftp.mkdir(nameDirectory)
            sftp.chdir(nameDirectory)
            copyssh(sftp,directory)
            sftp.chdir('..')
        ssh.close()

directoryList=getpaths(DIRPATH)
main()
