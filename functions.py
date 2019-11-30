import os
import sys
import logging
from ftplib import FTP

logger = logging.getLogger('logger')
logger.setLevel(logging.WARNING)
fileHandler = logging.FileHandler('test.log')
logger.addHandler(fileHandler)
formatter = logging.Formatter('%(asctime)s  %(levelname)s: %(message)s')
fileHandler.setFormatter(formatter)
logger.debug('This message should go to the log file')
logger.info('So should this')
logger.warning('And this, too')

#Récupération des variables définies dans le fichier de conf:
args=sys.argv
REPPATH=args[1]
METH=args[2]
NREP=args[3]
VERSIONNUMBER=args[4]


def getpaths(directoriesPath):
    directoryList=REPPATH.split(",")

    

