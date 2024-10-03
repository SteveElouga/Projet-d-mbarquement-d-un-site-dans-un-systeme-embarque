import os
from flask import jsonify
from page_web_systeme_embarque.extentions import app
from werkzeug.utils import secure_filename


def file_manage(file, folder):
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

    # Vérifie si le dossier spécifié existe, sinon le crée
    if not os.path.exists(app.config[folder]):
        os.makedirs(app.config[folder])

    # Crée le chemin absolu pour le fichier et l'enregistre
    file_url = os.path.abspath(os.path.join(
        app.config[folder], filename))
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
    Crée l'URL du fichier en fonction de son type (image, texte, musique, vidéo, PDF, ou autre).
    - Cette fonction dirige le fichier vers un dossier approprié selon son extension.
    - Chaque type de fichier est enregistré dans un dossier distinct.

    Args:
        file: Le fichier à traiter.

    Returns:
        file_url: L'URL du fichier enregistré.
    """
    
    # Définit les extensions autorisées pour chaque type de fichier
    ALLOWED_IMAGES_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_TEXT_EXTENSIONS = {'txt'}
    ALLOWED_MUSIC_EXTENSIONS = {'mp3'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4'}
    ALLOWED_PDF_EXTENSIONS = {'pdf'}

    # Vérifie si le fichier est une image et l'enregistre dans le dossier approprié
    if (allowed_file(file.filename, ALLOWED_IMAGES_EXTENSIONS)):
        file_url = file_manage(file, "UPLOAD_IMAGE_FOLDER")
        return file_url
    # Vérifie si le fichier est un fichier texte
    elif (allowed_file(file.filename, ALLOWED_TEXT_EXTENSIONS)):
        file_url = file_manage(file, "UPLOAD_TEXT_FOLDER")
        return file_url
     # Vérifie si le fichier est un fichier audio
    elif (allowed_file(file.filename, ALLOWED_MUSIC_EXTENSIONS)):
        file_url = file_manage(file, "UPLOAD_MUSIC_FOLDER")
        return file_url
     # Vérifie si le fichier est une vidéo
    elif (allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS)):
        file_url = file_manage(file, "UPLOAD_VIDEO_FOLDER")
        return file_url
    # Vérifie si le fichier est un PDF
    elif (allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS)):
        file_url = file_manage(file, "UPLOAD_PDF_FOLDER")
        return file_url
    # Si aucune extension ne correspond, le fichier est enregistré dans un dossier "autres"
    else:
        file_url = file_manage(file, "UPLOAD_ELSE_FOLDER")
        print(f'file_url: {file_url}')
        return file_url
