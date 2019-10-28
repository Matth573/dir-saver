import os
from ftplib import FTP

def getpaths(REPPATH):
    directoryList=REPPATH.split(",")
    for (dirpath in directoryList):
        os.chdir(dirpath)
        cmd="find . -name \* > " + "for" + dirpath
        os.system(cmd)
