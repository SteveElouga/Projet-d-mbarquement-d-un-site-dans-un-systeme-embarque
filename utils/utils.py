import os
import tempfile
from flask import jsonify
from werkzeug.utils import secure_filename
from appwrite.client import Client
from appwrite.services.storage import Storage
from page_web_systeme_embarque.extentions import app
from appwrite.input_file import InputFile

from page_web_systeme_embarque.models import Media

# Configuration AppWrite
client = Client()
client.set_endpoint(os.getenv('APPWRITE_ENDPOINT')
                    )  # Remplace par ton endpoint
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

    file.stream.seek(0)  # Remettre le pointeur du fichier au début
    # Vérifie si aucun fichier n'a été envoyé
    if file is None:
        return jsonify({"msg": "File not found"}), 400

    # Vérifie si le fichier n'a pas été sélectionné (nom vide)
    if file.filename == "":
        return jsonify({"msg": "No files selected"}), 400

     # Créer un fichier temporaire pour stocker le fichier
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Écrire le contenu dans le fichier temporaire
        temp_file.write(file.read())
        temp_file_path = temp_file.name  # Obtenir le chemin du fichier temporaire

    # Utiliser InputFile pour l'upload vers AppWrite
    input_file = InputFile.from_path(temp_file_path)

    media = Media.get_media_by_name(name=file.filename)

    if media is None:
        result = storage.create_file(
            bucket_id='6703157c0026f0d7caae',
            file_id='unique()',
            file=input_file
        )

        file_url = f"{os.getenv('APPWRITE_ENDPOINT')}/storage/buckets/{os.getenv(
            'BUCKET_ID')}/files/{result['$id']}/view?project={os.getenv('APPWRITE_PROJECT_ID')}"

        os.remove(temp_file_path)

        # Renvoie le chemin du fichier enregistré
        return file_url
    else:
        return media.media_url


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


def file_type(filename):
    """
    Cette fonction permet de recuperer le type d'un fichier dont le nom est passe en argument

    Args:
        file: Le nom fichier à traiter.

    Returns:
        type: Le type du fichier enregistré.
    """

    # Définit les extensions autorisées pour chaque "type" de fichier
    ALLOWED_IMAGES_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_TEXT_EXTENSIONS = {'txt'}
    ALLOWED_MUSIC_EXTENSIONS = {'mp3'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4'}
    ALLOWED_PDF_EXTENSIONS = {'pdf'}

    # Vérifie si le fichier est une image et retourne le type image
    if (allowed_file(filename, ALLOWED_IMAGES_EXTENSIONS)):
        return "image"
    # Vérifie si le fichier est un fichier texte
    elif (allowed_file(filename, ALLOWED_TEXT_EXTENSIONS)):
        return "text"     # Vérifie si le fichier est un fichier audio
    elif (allowed_file(filename, ALLOWED_MUSIC_EXTENSIONS)):
        return "audio"
     # Vérifie si le fichier est une vidéo
    elif (allowed_file(filename, ALLOWED_VIDEO_EXTENSIONS)):
        return "video"
    # Vérifie si le fichier est un PDF
    elif (allowed_file(filename, ALLOWED_PDF_EXTENSIONS)):
        return "pdf"
   # Si aucune extension ne correspond, le fichier est enregistré dans un dossier "else"
    else:
        return "else"


def get_files_per_type(medias, valid_extensions):
    files_list = []

    for media in medias:
        if media.name.endswith(valid_extensions):

            files_list.append(media)

    return files_list


def get_files_per_type_other(medias, valid_extensions):
    files_list = []

    for media in medias:
        if not media.name.endswith(valid_extensions):

            files_list.append(media)

    return files_list
