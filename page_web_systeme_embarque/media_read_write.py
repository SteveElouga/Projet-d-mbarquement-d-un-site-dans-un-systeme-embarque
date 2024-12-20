import logging as lg
import json
import os
from flask import Blueprint, request, jsonify

from .models import Media
from utils.utils import create_file_url, get_files_per_type, get_files_per_type_other, storage

from .schema import Media_schema

media_bp = Blueprint("media", __name__)


@media_bp.post("/add")
def add():
    """
    Ajoute un nouveau fichier média avec ses métadonnées (nom, description)
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Le fichier à télécharger
      - in: formData
        name: metadata
        type: string
        required: false
        description: Les informations JSON pour le média (nom et description)
    responses:
      201:
        description: Nouveau fichier ajouté
      409:
        description: Un fichier avec ce nom ou cette URL existe déjà
    """

    #  Valeur initiale de l'url d'un fichier
    file_url = {"url": "", "type": ""}

    # Récupère le fichier envoyé via 'form-data' sous la clé 'file'
    file = request.files['file']

    # Récupère les données supplémentaires envoyées sous la clé 'data' et les convertit en JSON
    data_json = request.form['metadata']
    # print(f'data_json: {data_json}')
    data = json.loads(data_json)
    # print(f'data: {data}')

    # Redéfinie l'url du fichier a enregistrer Génère l'URL où le fichier sera stocké

    # print(f'file_url: {str(file_url)}')
    file_url = create_file_url(file)
    media_name = file.filename

    # Si un fichier avec le même nom existe, retourne un message d'erreur avec un code 409
    media = Media.get_media_by_name(name=media_name)
    url_media = Media.get_media_by_url(url=file_url["url"])

    # Si un fichier avec le même nom ou avec la même URL existe, retourne un message d'erreur avec un code 409
    if media is not None:
        return jsonify({"msg": "Un fichier avec ce nom existe deja"}), 409
    elif url_media is not None:
        return jsonify({"msg": "Un fichier avec cette url existe deja"}), 409
    else:
        # Sinon, crée un nouvel objet Media avec les informations fournies
        new_media = Media(
            name=media_name,
            titre=data.get('titre').lower(),
            type=file_url["type"],
            description=data.get('description').lower(),
            media_url=file_url["url"]
        )
        # Enregistre le nouvel objet Media dans la base de données
        new_media.save()

    # Retourne un message de succès avec un code 201
    return jsonify({"msg": "Nouveau fichier ajoute"}), 201


@media_bp.get('/get')
def get_medias():
    """
    Récupère tous les fichiers médias stockés
    ---
    responses:
      200:
        description: Liste de tous les médias
        schema:
          type: object
          properties:
            msg:
              type: string
              description: Tous les medias
            result:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: ID du média
                  name:
                    type: string
                    description: Nom du média
                  type:
                    type: string
                    description: Type du média
                  description:
                    type: string
                    description: Description du média
                  media_url:
                    type: string
                    description: URL du média
                  created_at:
                    type: string
                    description: Date de creation du media
    """
    # Récupère tous les objets Media de la base de données
    medias = Media.query.all()

    if (len(medias) == 0):
        return jsonify({"msg": ["Aucun media"]}), 200

    # Sérialise les objets Media en JSON
    result = Media_schema().dump(medias, many=True)

    # Retourne la liste des médias avec un message de succès
    return jsonify({"msg": "Liste de tous les fichiers", "result": result}), 200


@media_bp.get('/get/<int:id>')
def get_medias_by_id(id):
    """
    Récupère un média spécifique par son ID
    ---
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID du média
    responses:
      200:
        description: Média trouvé
        schema:
          type: object
          properties:
            result:
              type: object
              properties:
                id:
                  type: integer
                  description: ID du média
                name:
                  type: string
                  description: Nom du média
                type:
                    type: string
                    description: Type du média
                description:
                  type: string
                  description: Description du média
                media_url:
                  type: string
                  description: URL du média
                created_at:
                  type: string
                  description: Date de creation du media
      404:
        description: Média non trouvé
    """

    # Récupère l'objet Media correspondant à l'ID donné
    media = Media.query.get(id)

    # Si le média n'existe pas, retourne un message d'erreur avec un code 404
    if media is None:
        return jsonify({"msg": "Ce fichier n'existe pas"}), 404

    # Sérialise l'objet Media en JSON
    result = Media_schema().dump(media)

    # Retourne les détails du média avec un code de succès 200
    return jsonify({"result": result}), 200


@media_bp.patch("/move/<int:id>")
def move_file_in_corbeille_by_id(id):
    """
    Recupere un média par son ID et le deplace dans le dossier corbeille
    ---
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID du média à deplacer
    responses:
      200:
        description: Média envoye dans la corbeille avec succès
      404:
        description: Média non trouvé / Le fichier n'existe pas dans le repertoire specifie
    """

    # Cette fonction depalce un fichier média par son ID et déplace son fichier associé dans un dossier corbeille

    # Récupère l'objet Media correspondant à l'ID donné
    media = Media.query.get(id)

    # Si le média n'existe pas, retourne un message d'erreur avec un code 404
    if media is None:
        return jsonify({"msg": "Ce fichier n'existe pas"}), 404

    # Vérifie si le fichier a supprimer existe, sinon il est créé
    if media.media_url:

        lg.error("Média envoye dans la corbeille avec succès")

        media.status = "pending"
        media.save()

        lg.warning(media.status)

        # Retourne un message de succès après suppression
        return jsonify({"msg": "Média envoye dans la corbeille avec succès"}), 200

    else:

        # Dans le cas ou le fichier a supprimer n'existe pas. supprimer le fichier de la base de données
        Media.delete_by_id(media)

        return jsonify({"msg": "Le fichier n'existe pas dans le repertoire specifie"}), 404


@media_bp.delete('/delete/<int:id>')
def delete_by_id(id):
    """
    Supprime definitivement un média par son ID
    ---
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID du média à supprimer
    responses:
      200:
        description: Média supprimé avec succès
      404:
        description: Média non trouvé / Le fichier n'existe pas dans le repertoire specifie
    """

    # Cette fonction Supprime un fichier média par son ID et déplace son fichier associé dans un dossier de suppression supp_folder

    # Récupère l'objet Media correspondant à l'ID donné
    media = Media.query.get(id)

    # Si le média n'existe pas, retourne un message d'erreur avec un code 404
    if media is None:
        return jsonify({"msg": "Ce fichier n'existe pas"}), 404

    url = media.media_url

    # Vérifie si le fichier a supprimer existe, sinon il est créé
    if url:
      
        file_id = url.split('/files/')[1].split('/view')[0]
      
        storage.delete_file(os.getenv(
            'BUCKET_ID'), file_id)

        # Supprime l'enregistrement du média de la base de données
        Media.delete_by_id(media)

        lg.warning("Média supprimé avec succès")

        # Retourne un message de succès après suppression
        return jsonify({"msg": "Média supprimé avec succès"})

    else:
        return jsonify({"msg": "Le fichier n'existe pas dans le repertoire specifie"}), 404


@media_bp.patch("/restaure/<int:id>")
def restaure_media_by_id(id):
    """
    Restaure un media par son ID
    ---
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID du média à restaurer
    responses:
      200:
        description: Média resraure
      404:
        description: Ce fichier n'existe pas / Impossible de restaurer ce fichier
    """

    # Cette fonction restaure un fichier média par son ID

    # Récupère l'objet Media correspondant à l'ID donné
    media = Media.query.get(id)

    # Si le média n'existe pas, retourne un message d'erreur avec un code 404
    if media is None:
        return jsonify({"msg": "Ce fichier n'existe pas"}), 404

    if media.status == "pending":

        media.status = "restaure"
        media.save()

        lg.warning("Média restaure avec succès")

        # Retourne un message de succès après suppression
        return jsonify({"msg": "Média restaure avec succès"}), 200

    else:

        return jsonify({"msg": "Impossible de restaurer ce fichier"}), 404

@media_bp.get("/get/images")
def get_images():
    """
      Récupère toutes les images stockés
      ---
      responses:
        200:
          description: Liste de toutes les images
          schema:
            type: object
            properties:
              msg:
                type: string
                description: Toutes les images
              result:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: ID du média
                    name:
                      type: string
                      description: Nom du média
                    type:
                      type: string
                      description: Type du média
                    description:
                      type: string
                      description: Description du média
                    media_url:
                      type: string
                      description: URL du média
                    created_at:
                      type: string
                      description: Date de creation du media
        400:
          description: Aucune image pour l'instant               
    """
    medias = Media.query.all()
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif')
    files_list = get_files_per_type(medias, valid_extensions)
    new_medias = []
    
    for media in files_list:
      if media.status != 'pending':
        new_medias.append(media)

    # Sérialise les objets Media en JSON
    result = Media_schema().dump(new_medias, many=True)

    if len(new_medias) > 0:

        # Retourne la liste des médias avec un message de succès
        return jsonify({"msg": "Liste de toutes les images", "result": result}), 200

    return jsonify({"msg": "Aucune image pour l'instant"}), 404


@media_bp.get("/get/pdf")
def get_pdf_files():
    """
      Récupère tous les fichiers pdf
      ---
      responses:
        200:
          description: Liste de tous les fichiers pdf
          schema:
            type: object
            properties:
              msg:
                type: string
                description: Tous les pdf
              result:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: ID du média
                    name:
                      type: string
                      description: Nom du média
                    type:
                      type: string
                      description: Type du média
                    description:
                      type: string
                      description: Description du média
                    media_url:
                      type: string
                      description: URL du média
                    created_at:
                      type: string
                      description: Date de creation du media
        400:
          description: Aucun pdf pour l'instant                  
    """

    medias = Media.query.all()
    valid_extensions = ('.pdf')

    files_list = get_files_per_type(medias, valid_extensions)
    new_medias = []
    
    for media in files_list:
      if media.status != 'pending':
        new_medias.append(media)

    # Sérialise les objets Media en JSON
    result = Media_schema().dump(new_medias, many=True)

    if len(new_medias) > 0:

        # Retourne la liste des médias avec un message de succès
        return jsonify({"msg": "Liste de tous les fichiers pdf", "result": result}), 200

    return jsonify({"msg": "Aucun pdf pour l'instant"}), 404


@media_bp.get("/get/videos")
def get_videos():
    """
      Récupère toutes les videos
      ---
      responses:
        200:
          description: Liste de toutes les videos
          schema:
            type: object
            properties:
              msg:
                type: string
                description: Toutes les videos
              result:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: ID du média
                    name:
                      type: string
                      description: Nom du média
                    type:
                      type: string
                      description: Type du média
                    description:
                      type: string
                      description: Description du média
                    media_url:
                      type: string
                      description: URL du média
                    created_at:
                      type: string
                      description: Date de creation du media
        400:
          description: Aucune video pour l'instant               
    """
    medias = Media.query.all()
    valid_extensions = ('.mp4')
    
    files_list = get_files_per_type(medias, valid_extensions)
    new_medias = []
    
    for media in files_list:
      if media.status != 'pending':
        new_medias.append(media)

    # Sérialise les objets Media en JSON
    result = Media_schema().dump(new_medias, many=True)

    if len(new_medias) > 0:

        # Retourne la liste des médias avec un message de succès
        return jsonify({"msg": "Liste de toutes les videos", "result": result}), 200

    return jsonify({"msg": "Aucune video pour l'instant"}), 404

@media_bp.get("/get/audios")
def get_audios():
    """
      Récupère tous les audios
      ---
      responses:
        200:
          description: Liste de tous les audios
          schema:
            type: object
            properties:
              msg:
                type: string
                description: Tous les audios
              result:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: ID du média
                    name:
                      type: string
                      description: Nom du média
                    type:
                      type: string
                      description: Type du média
                    description:
                      type: string
                      description: Description du média
                    media_url:
                      type: string
                      description: URL du média
                    created_at:
                      type: string
                      description: Date de creation du media
        400:
          description: Aucun fichier audio pour l'instant              
    """
    medias = Media.query.all()
    valid_extensions = ('.mp3')
    
    files_list = get_files_per_type(medias, valid_extensions)
    new_medias = []
    
    for media in files_list:
      if media.status != 'pending':
        new_medias.append(media)

    # Sérialise les objets Media en JSON
    result = Media_schema().dump(new_medias, many=True)

    if len(new_medias) > 0:

        # Retourne la liste des médias avec un message de succès
        return jsonify({"msg": "Liste de tous les audios", "result": result}), 200

    return jsonify({"msg": "Aucun fichier audio pour l'instant"}), 404

@media_bp.get("/get/texts")
def get_texts():
    """
      Récupère tous les fichiers texts
      ---
      responses:
        200:
          description: Liste de tous les fichiers texts
          schema:
            type: object
            properties:
              msg:
                type: string
                description: Tous les fichiers texts
              result:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: ID du média
                    name:
                      type: string
                      description: Nom du média
                    type:
                      type: string
                      description: Type du média
                    description:
                      type: string
                      description: Description du média
                    media_url:
                      type: string
                      description: URL du média
                    created_at:
                      type: string
                      description: Date de creation du media
        404:              
          description: "Aucun fichier text pour l'instant"              
    """
    medias = Media.query.all()
    valid_extensions = ('.txt')
    
    files_list = get_files_per_type(medias, valid_extensions)
    new_medias = []
    
    for media in files_list:
      if media.status != 'pending':
        new_medias.append(media)

    # Sérialise les objets Media en JSON
    result = Media_schema().dump(new_medias, many=True)

    if len(new_medias) > 0: 

        # Retourne la liste des médias avec un message de succès
        return jsonify({"msg": "Liste de tous les fichiers texts", "result": result}), 200

    return jsonify({"msg": "Aucun fichier text pour l'instant"}), 404

@media_bp.get("/get/other")
def get_other():
    """
      Récupère tous les fichiers non identifies
      ---
      responses:
        200:
          description: Liste de tous les fichiers non identifies
          schema:
            type: object
            properties:
              msg:
                type: string
                description: Tous les fichiers non identifies
              result:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: ID du média
                    name:
                      type: string
                      description: Nom du média
                    type:
                      type: string
                      description: Type du média
                    description:
                      type: string
                      description: Description du média
                    media_url:
                      type: string
                      description: URL du média
                    created_at:
                      type: string
                      description: Date de creation du media
        404:              
          description: "Aucun fichier non identifie pour l'instant"              
    """
    medias = Media.query.all()
    valid_extensions = ('.txt', '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.mp3', '.mp4')
    
    files_list = get_files_per_type_other(medias, valid_extensions)

    new_medias = []
    
    for media in files_list:
      if media.status != 'pending':
        new_medias.append(media)

    # Sérialise les objets Media en JSON
    result = Media_schema().dump(new_medias, many=True)

    if len(new_medias) > 0:

        # Retourne la liste des médias avec un message de succès
        return jsonify({"msg": "Liste de tous les fichiers non identifies", "result": result}), 200

    return jsonify({"msg": "Aucun fichier non identifie pour l'instant"}), 404

@media_bp.get("/get/corbeille")
def get_corbeille():
    """
      Récupère tous les fichiers qui sont dans la corbeille
      ---
      responses:
        200:
          description: Liste de tous les fichiers qui sont dans la corbeille
          schema:
            type: object
            properties:
              msg:
                type: string
                description: Tous les fichiers qui sont dans la corbeille
              result:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: ID du média
                    name:
                      type: string
                      description: Nom du média
                    type:
                      type: string
                      description: Type du média
                    description:
                      type: string
                      description: Description du média
                    media_url:
                      type: string
                      description: URL du média
                    created_at:
                      type: string
                      description: Date de creation du media
        404:              
          description: "Aucun fichier dans la corbeille pour l'instant"              
    """
    medias = Media.query.all()
    
    corbeille = []
    
    for media in medias:
      if media.status == 'pending':
        corbeille.append(media)

    # Sérialise les objets Media en JSON
    result = Media_schema().dump(corbeille, many=True)

    if len(corbeille) > 0:

        # Retourne la liste des médias avec un message de succès
        return jsonify({"msg": "Liste de tous les fichiers qui sont dans la corbeille", "result": result}), 200

    return jsonify({"msg": "Aucun fichier dans la corbeille pour l'instant"}), 404

