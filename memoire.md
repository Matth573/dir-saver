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

Une fois dans le bon dossier, l'application appel la fonction "version_handler" qui s'occupe de vérifier comment nommer le dossier de sauvegarde et s'il faut gérer le nombre de dossier. Une fois le nouveau dossier crée, l'application appel la bonne fonction de copie.

## Liste des variables : 

### Variables globales:

