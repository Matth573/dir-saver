import os
import sys
import logging

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
fileHandler = logging.FileHandler('test.log')
logger.addHandler(fileHandler)
formatter = logging.Formatter('%(asctime)s  %(levelname)s: %(message)s')
fileHandler.setFormatter(formatter)

#Récupération des variables définies dans le fichier de conf:
args=sys.argv
REPPATH=args[1]
METH=args[2]
IP_URL_ADDRESS=args[3]
LOGIN=args[4]
PASSWORD=args[5]
NREP=args[6]
VERSIONNUMBER=args[7]


def getpaths(directoriesPath):
    directoryList=REPPATH.split(",")

from os import walk
import shutil
def localCopy(src,dest):
    logger.info("Copy du dossier")
    src='/Users/matthieu/Documents/Telecom/Semestre 7/Scripting System/test'
    dest='/Users/matthieu/Documents/Telecom/Semestre 7/Scripting System/test6'
    destination = shutil.copytree(src,dest)
    print(destination)
from ftplib import FTP
def ftpcopy(adresse,login,mdp):
    with FTP(adresse,login,mdp) as ftp:
        print(ftp.dir())
import os
#ftpcopy(IP_URL_ADDRESS,LOGIN,PASSWORD)
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

with FTP(IP_URL_ADDRESS,LOGIN,PASSWORD) as ftp:
    ftp.mkd("test1")
    ftp.cwd('test1')
    copyftp(ftp,"/Users/matthieu/Documents/Telecom/Semestre 7/inforx/Scripting System/test")

