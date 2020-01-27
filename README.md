

# directory-saver

directory-saver est une application qui vous permet de sauvegarder des dossiers sur un serveur distant ( en utilisant les protocoles FTP, FTPS ou SFTP ) ou en locale.

Il vous est possible de gérer le nombre de sauvegarde à garder dans la destination, de recevoir un mail récapitulatif après la sauvegarde et d'automatiser le processus.

## Installation :

Le logiciel nécessite les dépendances suivantes:

- python3
- configparser
- ftplib
- smtplib
- paramiko
- nano



Pour commencer à utiliser l'application, il faut remplir le fichier de configuration "config.ini" cf partie suivante.

Une fois le fichier remplie, il suffit d'exécuter le script bash : "directory_saver.sh"

## Configuration : 

ip_url_address : l'url ou l'adresse ip du serveur sur lequel se fera la sauvegarde  

login, password : le nom d'utilisateur et le mot de passe pour se connecter au serveur.

with_ftp, with_ftps, with_sftp, with_local_save : un seul de ces quatre champs doit être sur "on", les 3 autres sur "off". Le champ sur "on" indiquera à l'application quelle protocole utiliser pour faire la sauvegarde.

directories_to_save : La liste des chemins absolus, séparés par une virgule, des dossiers à sauvegarder.

backup_directory : Le chemin absolu dans la destination où les sauvegarde seront enregistrés. ATTENTION : Si le dossier n'existe pas, l'application tentera de créer les dossier manquant pour effectuer la sauvegarde. Vous devez donc avoir les droits pour créer des répertoires dans la destination si le chemin n'existe pas déjà.

version_control : Mettez le sur "on" si vous voulez limiter le nombre de sauvegarde à enregistrer dans la destination. Sur "off" sinon.

version_number : Le nombre de sauvegarde maximale que doit contenir la destination.

format : Indique comment doivent être nommé les dossier de sauvegarde. "date" pour que la date et l'heure de la sauvegarde soit le nom du fichier. "number" si le numéro de la sauvegarde doit être le nom du fichier. ATTENTION : pour changer de format alors que des sauvegardes ont déjà été effectuée, il faut effacer toutes les sauvegardes précédentes.

get_mail : Mettez le sur "on" si vous voulez recevoir un mail résumant la sauvegarde à la fin de cell-ci. Sur "off" sinon.

log_attached : Mettez le sur "on" si vous voulez que le fichier log de l'application soit attaché au mail.

smtp_host : url du serveur smtp pour envoyer le mail.

smtp_port : port du serveur smtp

smtp_host_email_address : mail de l'expéditeur 

smtp_password : mot de passe pour se connecter au serveur smtp

send_to : adresse du destinataire

## Automatisation de la sauvegarde

Vous pouvez automatiser la sauvegarde en lançant automatiquement le script bash grâce à cron:

Lancer la commande suivante pour modifier la crontab.

```bash
EDITOR=nano crontab -e
```

Pour lancer la sauvegarde tous les jour, entrez la ligne suivantes : 

```
@daily ./direcotry_saver.sh >> /dev/null
```

Pour lancer la sauvegarde une fois par semaine, entrez la ligne suivante:

```
@weekly ./direcotry_saver.sh >> /dev/null
```

Pour quitter l'édition de la crontab, appuyez sur CTRL + x

### Pour plus de renseignement:

La crontab permet également de spécifié à quelle heure ou quelle jour exactement vous souhaitez exécuter la sauvegarde. Pour de plus ample information vous pouvez suivre le lien suivant :

https://fr.wikipedia.org/wiki/Cron