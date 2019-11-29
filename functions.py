import os
import sys
import logging
from ftplib import FTP

logging.basicConfig(filename='example.log',level=logging.DEBUG)
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')

#Récupération des variables définies dans le fichier de conf:
args=sys.argv
REPPATH=args[1]
METH=args[2]
NREP=args[3]
VERSIONNUMBER=args[4]


def getpaths(directoriesPath):
    directoryList=REPPATH.split(",")

    

