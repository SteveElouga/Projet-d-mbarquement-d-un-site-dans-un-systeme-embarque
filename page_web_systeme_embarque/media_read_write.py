import os
import logging as lg
import json
import shutil
from flask import Blueprint, request, jsonify, send_from_directory
from flasgger import Swagger

from .models import Media
from .extentions import app
from utils.utils import create_file_url, file_type

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
    # print(f'file: {len(file.read())}')

    # Récupère les données supplémentaires envoyées sous la clé 'data' et les convertit en JSON
    data_json = request.form['metadata']
    # print(f'data_json: {data_json}')
    data = json.loads(data_json)
    # print(f'data: {data}')

    # Redéfinie l'url du fichier a enregistrer Génère l'URL où le fichier sera stocké
    file_url = create_file_url(file)
    # print(f'file_url: {str(file_url)}')

    # Si un fichier avec le même nom existe, retourne un message d'erreur avec un code 409
    media = Media.get_media_by_name(name=data.get('name'))
    url_media = Media.get_media_by_url(url=file_url["url"])
    media_name = file.filename
    # print(f'url_media: {url_media}')

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
            # media_url=file_url["url"]
            media_url=url_media
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

    # Vérifie si le fichier a supprimer existe, sinon il est créé
    if media.media_url:

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
