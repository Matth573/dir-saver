# Mémoire technique : directory-saver

L'application se compose en 3 fichiers python et un fichier de configuration.

Le gros de l'application se fait dans le fichier "functions.py". Après avoir récupéré les informations spécifiées dans le fichier de configuration, l'application vérifie que les informations nécessaire sont bien renseignées (ceci est effectuée dans le fichier "verif-config.py"). Si c'est le cas la sauvegarde se lance. L'appel aux fonctions présent dans "mail_function.py" se lance ensuite si l'utilisateur l'a spécifié dans le fichier de configuration.

## functions.py

Après l'import des libraries nécessaires, le logger est initialisé et stocké dans la variable LOGGER.

Puis le parser du fichier de configuration est appelé et les variables globales correspondants aux choix de l'utilisateur sont créées.

On retrouve ensuite la déclaration des fonctions utiles à la sauvegarde. Elles sont triées par leur fonctionnalité.

### main

Le main se décompose en deux parties. La première crée l'objet selon le protocole utilisé et se déplace dans le système de fichier jusqu'au répertoire où sont stockées les sauvegarde. La seconde crée le nouveau répertoire de sauvegarde et copie les dossiers à copier dans la destination.

#### Connexion au serveur

En fonction de la valeur des variables globales "WITH_...", qui indiquent le protocole à utiliser, l'application instancie le bon objet pour communiquer avec le serveur. Pour une sauvegarde en locale, l'application donne à la variable qui accueil le client la valeur "None".

Une fois la connexion effectué, l'application appelle la fonction correspondant au bon protocole pour se déplacer là où sont stockées les sauvegardes.

Pour se faire, l'application se déplace dans le système de fichier dossier par dossier, et crée les répertoires manquant s'il le faut, sauf pour les sauvegardes en locale où les dossiers doivent déjà exister.

Pour la connexion via SFTP, OpenMediaVault place les dossier partagé dans le répertoire "/sharedfolders", l'application se place donc là avant d'appeler la fonction "go_to_direcory_sftp"

#### Création du dossier et copie

Une fois dans le bon dossier, l'application appel la fonction "version_handler" qui s'occupe de vérifier comment nommer le dossier de sauvegarde et s'il faut gérer le nombre de dossier. Une fois le nouveau dossier crée, l'application crée un répertoire pour chaque dossier spécifié par l'utilisateur et appelle la bonne fonction de copie. 



Une fois sortie du main, l'application reconnait si la copie est bien effectué en lisant le fichier de log généré. Si un warning est présent, c'est que tout ne s'est pas bien passé.

Si l'utilisateur a demandé de recevoir un mail, l'application appelle ensuite la fonction *success* ou *failure* du fichier "mail_function.py".

## mail_function.py

Le module mail_function se compose d'une fonction principale *send_mail* qui prend en paramètre un objet et un corps et qui envoie le mail correspondant en utilisant la configuration spécifié par l'utilisateur.

Les deux fonctions *success* et *failure* adapte l'objet et le corps à donner à la fonction *send_mail* pour correspondre à la réussite ou à l'échec de la copie.

Pour donner plus d'indication dans le mail, la fonction success va copier les dernière ligne du fichier log pour les incorporer au corps du mail.

## verif_config.py

Le module "verif_config.py" vérifie qu'une seule méthode de transfert est spécifié dans le fichier de configuration et que le nom à donner aux sauvegardes est bien "number" ou "date".

## Liste des variables : 

### Variables globales:

- CONFIG : La variable qui contient l'objet ConfigParser
- DIRECTORIES_TO_SAVE : les répertoires à sauvegarder tels qu'indiqué par l'utilisateur 
- WITH_FTP, WITH_FTPS, WITH_SFTP, WITH_LOCAL_SAVE : booléens correspondant au choix de méthode de sauvegarde de l'utilisateur.
- IP_URL_ADDRESS : adresse ip ou url du serveur tel qu'indiqué par l'utilisateur
- LOGIN, PASSWORD : Identifiants et mot de passe pour se connecter au serveur, tels qu'indiqués par l'utilisateur
- BACKUP_DIRECTORY : Le chemin où doivent être enregistré les sauvegardes dans la destination.
- VERSION_CONTROL : booléen correpondant que choix de l'utilisateur de restreindre le nombre de sauvegarde dans la destination
- VERSION_NUMBER : le nombre de sauvegarde à garder
- VERSION_FORMAT : le format à donner aux noms des dossiers de sauvegarde
- MAIL_ON : booléen correpondant que choix de l'utilisateur d'envoyer un mail après l'exécution de l'application ou non
- nb_file_save : le nombre de fichier sauvegardé dans la destination
- name_directory : le nom donné au dossier qui contient la sauvegarde 
- directory_removed : le nom du dossier de la sauvegarde qui a été supprimée si le maximum de sauvegarde étai atteint

## copy_ftp, copy_sftp

- ftp, sftp : la variable contenant l'objet FTP, FTP_TLS ou SFTP utilisé pour interagir avec le serveur 
- path : le chemin du répertoire à copier
- name : le nom des éléments du répertoires en cours de copie
- localpath : le chemin de l'élément en cours de copie

## remove_ftp_dir

- 