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
PASSWORD=[5]
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


