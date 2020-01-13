import os
import sys
import logging
import paramiko

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
fileHandler = logging.FileHandler('test.log')
logger.addHandler(fileHandler)
formatter = logging.Formatter('%(asctime)s  %(levelname)s: %(message)s')
fileHandler.setFormatter(formatter)

#Récupération des variables définies dans le fichier de conf:
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
    directoryList=REPPATH.split(",")

from os import walk
import shutil
def localCopy(src,dest):
    logger.info("Copie du dossier")
    src='/Users/matthieu/Documents/Telecom/Semestre 7/Scripting System/test'
    dest='/Users/matthieu/Documents/Telecom/Semestre 7/Scripting System/test6'
    destination = shutil.copytree(src,dest)
    print(destination)

from ftplib import FTP,FTP_TLS
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

class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source, target):
        ''' Uploads the contents of the source directory to the target path. The
            target directory needs to exists. All subdirectories in source are 
            created under target.
        '''
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        ''' Augments mkdir by adding an option to not fail if the folder exists  '''
        try:
            super(MySFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise

def goToDirectory(ftp,path):
    listdir=path.split('/')
    if listdir[0]=='':
        listdir.remove('')
    for directory in listdir:
        if not directory in ftp.nlst():
            ftp.mkd(directory)
        ftp.cwd(directory)

#client = paramiko.SSHClient()
#client.load_system_host_keys()
#client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
#client.connect(hostname, 21, username, password)

if METH == "FTPS" :
    with FTP_TLS(IP_URL_ADDRESS,LOGIN,PASSWORD,SAVEPATH) as ftp:
        goToDirectory(ftp,SAVEPATH)
        copyftp(ftp,DIRPATH)
if METH == "FTP" : 
    with FTP(IP_URL_ADDRESS,LOGIN,PASSWORD,SAVEPATH) as ftp:
        goToDirectory(ftp,SAVEPATH)
        copyftp(ftp,DIRPATH)
if METH == "SFTP":
    transport = paramiko.Transport((IP_URL_ADDRESS, 22))
    transport.connect(username=LOGIN, password=PASSWORD)
    sftp = MySFTPClient.from_transport(transport)
    sftp.mkdir(SAVEPATH + "/test", ignore_existing=True)
    sftp.put_dir(DIRPATH, SAVEPATH + "/test")
    sftp.close()
