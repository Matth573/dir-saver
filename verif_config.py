import configparser


def config_init():
    config = configparser.RawConfigParser()
    config.read('config.ini')
    return config


def main():
    CONFIG = config_init()
    WITH_FTP = CONFIG.getboolean('save_method', 'with_ftp')
    WITH_FTPS = CONFIG.getboolean('save_method', 'with_ftps')
    WITH_SFTP = CONFIG.getboolean('save_method', 'WITH_SFTP')
    WITH_LOCAL_SAVE = CONFIG.getboolean('save_method', 'with_local_save')
    methods = [WITH_FTP, WITH_FTPS, WITH_SFTP, WITH_LOCAL_SAVE]
    counter = 0
    for method in methods:
        if method:
            counter = counter + 1
    if counter != 1:
        return "Une seule méthode de sauvegarde doit être utilisé."
    FORMAT = CONFIG.get('version_handler', 'format')
    if FORMAT != "date" and FORMAT != "number":
        return "Le format du nom de dossier est soit 'number', soit 'date'"
    return "ok"
