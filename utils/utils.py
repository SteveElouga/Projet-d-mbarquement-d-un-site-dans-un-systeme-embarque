import os
from flask import jsonify
from page_web_systeme_embarque.extentions import app
from werkzeug.utils import secure_filename
from appwrite.client import Client
from appwrite.services.storage import Storage

# Configuration AppWrite
client = Client()
client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))  # Remplace par ton endpoint
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))

storage = Storage(client)

def file_manage(file):
    """
    Gère l'enregistrement d'un fichier dans le dossier spécifié en fonction de son extension.
    - Si le fichier est absent ou non sélectionné, renvoie un message d'erreur avec un code 400.
    - Crée un chemin sécurisé pour le fichier et l'enregistre dans le dossier approprié.
    - Si le dossier n'existe pas, il est créé automatiquement.

    Args:
        file: Le fichier à gérer.
        folder: Le nom du dossier où enregistrer le fichier (doit être une clé dans `app.config`).

    Returns:
        file_url: Le chemin absolu où le fichier a été enregistré.
    """
    # Vérifie si aucun fichier n'a été envoyé
    if file is None:
        return jsonify({"msg": "File not found"}), 400

    # Vérifie si le fichier n'a pas été sélectionné (nom vide)
    if file.filename == "":
        return jsonify({"msg": "No files selected"}), 400

    # Génère un nom de fichier sécurisé pour éviter les injections de chemin
    filename = secure_filename(filename=file.filename)
    
    # Upload to AppWrite
    result = storage.create_file(bucket_id='6703157c0026f0d7caae', file_id='unique()', file=file)
    file_url = f"{os.getenv('APPWRITE_ENDPOINT')}/storage/buckets/os.getenv('BUCKET_ID')/files/{result['$id']}/view?project={os.getenv('APPWRITE_PROJECT_ID')}"
    file.save(file_url)

    # Renvoie le chemin du fichier enregistré
    return file_url


def allowed_file(filename, allowed_extensions):
    """
    Vérifie si un fichier a une extension autorisée.

    Args:
        filename: Le nom du fichier à vérifier.
        allowed_extensions: Un ensemble d'extensions autorisées.

    Returns:
        bool: True si l'extension du fichier est autorisée, False sinon.
    """

    # Vérifie si le nom de fichier contient une extension et si cette extension est dans les extensions autorisées
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def create_file_url(file):
    """
    Crée l'URL du fichier en fonction de son "type" (image, texte, musique, vidéo, PDF, ou autre).
    - Cette fonction dirige le fichier vers un dossier approprié selon son extension.
    - Chaque "type" de fichier est enregistré dans un dossier distinct.

    Args:
        file: Le fichier à traiter.

    Returns:
        file_url: L'URL du fichier enregistré.
    """

    # Définit les extensions autorisées pour chaque "type" de fichier
    ALLOWED_IMAGES_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_TEXT_EXTENSIONS = {'txt'}
    ALLOWED_MUSIC_EXTENSIONS = {'mp3'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4'}
    ALLOWED_PDF_EXTENSIONS = {'pdf'}
        
    file_url = file_manage(file)

    # Vérifie si le fichier est une image et l'enregistre dans le dossier approprié
    if (allowed_file(file.filename, ALLOWED_IMAGES_EXTENSIONS)):
        return {"url": file_url, "type": "image"}
    # Vérifie si le fichier est un fichier texte
    elif (allowed_file(file.filename, ALLOWED_TEXT_EXTENSIONS)):
        return {"url": file_url, "type": "text"}
     # Vérifie si le fichier est un fichier audio
    elif (allowed_file(file.filename, ALLOWED_MUSIC_EXTENSIONS)):
        return {"url": file_url, "type": "audio"}
     # Vérifie si le fichier est une vidéo
    elif (allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS)):
        return {"url": file_url, "type": "video"}
    # Vérifie si le fichier est un PDF
    elif (allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS)):
        return {"url": file_url, "type": "pdf"}
    # Si aucune extension ne correspond, le fichier est enregistré dans un dossier "autres"
    else:
        print(f'file_url: {file_url}')
        return {"url": file_url, "type": "else"}


