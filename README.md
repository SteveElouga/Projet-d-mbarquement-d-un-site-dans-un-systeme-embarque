# Media File Management API

Cette application Flask permet de gérer des fichiers médias et leurs métadonnées via une API REST. Les fonctionnalités incluent l'ajout de fichiers, la récupération des fichiers stockés, la récupération par ID, et la suppression de fichiers. Les fichiers peuvent être de différents types (images, vidéos, textes, PDF, musique, etc...), chacun étant enregistré dans un dossier approprié.

## Fonctionnalités

### 1. Ajout de fichier média (POST /add) :
- Ajoute un fichier avec son nom, sa description et génère un type et une URL où le fichier sera stocké.
- Vérifie si un fichier avec le même nom ou la même URL existe déjà.
- Si le fichier est unique, il est enregistré et ajouté à la base de données.

### 2. Récupération de tous les fichiers médias (GET /get) :
- Récupère et renvoie une liste de tous les fichiers médias stockés dans la base de données.

### 3. Récupération d'un fichier média par ID (GET /get/<id>) :
- Récupère un fichier média spécifique via son ID.
- Si le fichier n'existe pas, un message d'erreur est retourné.

### 4. Suppression d'un fichier média par ID (DELETE /delete/<id>) :
- Supprime definitivement un fichier média spécifique et déplace son fichier physique dans un dossier de suppression.

## Installation

### 1. Clonez le repository :

```bash
git clone https://github.com/SteveElouga/Projet-d-mbarquement-d-un-site-dans-un-systeme-embarque.git
```

### 2. Accédez au répertoire du projet :

```bash
cd votre-projet

```

### 3. Installez les dépendances :

```bash
pip install -r requirements.txt
```

### 4. Configurez les variables dans config.py :

 - UPLOAD_IMAGE_FOLDER
 - UPLOAD_TEXT_FOLDER
 - UPLOAD_MUSIC_FOLDER
 - UPLOAD_VIDEO_FOLDER
 - UPLOAD_PDF_FOLDER
 - UPLOAD_ELSE_FOLDER
 - SUPP_FOLDER

### 5. Exécutez l’application Flask :

```bash
export FLASK_APP=run.py
flask run
```

## Endpoints

## POST /add

Ajoute un nouveau fichier média avec des métadonnées.

- Requête (form-data) :
- file: Fichier à ajouter.
- data: JSON contenant le nom et la description du fichier.
- Réponse :
- 201: Nouveau fichier ajouté.
- 409: Un fichier avec ce nom existe deja / Un fichier avec cette url existe deja

## GET /get

Récupère la liste de tous les fichiers médias.

- Réponse :
- 200: Liste de tous les fichiers.

## GET /get/id

Récupère un fichier média spécifique par son ID.

- Réponse :
- 200: result.
- 404: Ce fichier n'existe pas.

## DELETE /move/id

Supprime un fichier média spécifique.

- Réponse :
- 200: Média envoye dans la corbeille avec succès.
- 404: Média non trouvé / Le fichier n'existe pas dans le repertoire specifie.

## DELETE /delete/id

Supprime un fichier média spécifique.

- Réponse :
- 200: Média supprimé avec succès.
- 404: Média non trouvé / Le fichier n'existe pas dans le repertoire specifie.

## Gestion des fichiers

Les fichiers sont enregistrés dans des dossiers basés sur leur type (image, texte, vidéo, etc...) grâce à la fonction create_file_url. Chaque extension de fichier est gérée pour être enregistrée dans un dossier spécifique.

## Contribuer

- Forkez le projet
- Créez une branche de fonctionnalité (git checkouinterface=wlan0
driver=nl80211
ssid=MediasAppAP
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=TonMotDePasse
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMPt -b feature/new-feature)
- Committez vos changements (git commit -m 'Add some feature')
- Poussez à la branche (git push origin feature/new-feature)
- Créez une nouvelle Pull Request

## License

Ce projet est sous licence ENSPD.

## Auteur

Réalisé par @elouganyobe nyobeelouga5@gmail.com

hostapd.service - Access point and authentication server for Wi-Fi and Ethern>
     Loaded: loaded (/lib/systemd/system/hostapd.service; enabled; preset: enab>
     Active: failed (Result: exit-code) since Sun 2024-10-20 21:11:47 WAT; 1min>
       Docs: man:hostapd(8)
    Process: 6429 ExecStart=/usr/sbin/hostapd -B -P /run/hostapd.pid $DAEMON_OP>
        CPU: 20ms

Oct 20 21:11:47 raspberrypi systemd[1]: hostapd.service: Scheduled restart job,>
Oct 20 21:11:47 raspberrypi systemd[1]: Stopped hostapd.service - Access point >
Oct 20 21:11:47 raspberrypi systemd[1]: hostapd.service: Start request repeated>
Oct 20 21:11:47 raspberrypi systemd[1]: hostapd.service: Failed with result 'ex>
Oct 20 21:11:47 raspberrypi systemd[1]: Failed to start hostapd.service - Acces>
lines 1-12/12 (END)
