import os
import sys
import logging
import paramiko
import pdb
from datetime import datetime

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

def removeDirectorySSH(ssh, path):
    for item in ssh.listdir(path):
        if item in ['.', '..']:
            continue
        else:
            lstatout = str(ssh.lstat(item)).split()[0]
            if 'd' in lstatout:
                removeDirectorySSH(ssh,item)
                ssh.rmdir(item)
            else:
                ssh.remove(item)

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
        ssh = ssh.open_sftp()
        ssh.chdir("/sharedfolders/")
        goToDirectorySSH(ssh,SAVEPATH)
        if len(ssh.listdir()) >= int(VERSIONNUMBER):
            removeDirectorySSH(ssh,ssh.listdir()[0])
        d=datetime.now()
        ssh.mkdir(str(d))
        ssh.chdir(str(d))
        for directory in directoryList:
            logger.info("Copie du dossier : "+directory)
            nameDirectory = directory.split('/')[-1]
            ssh.mkdir(nameDirectory)
            ssh.chdir(nameDirectory)
            copyssh(ssh,directory)
            ssh.chdir('..')
        ssh.close()

directoryList=getpaths(DIRPATH)
main()
