import os
import logging as lg
import json
import shutil
from flask import Blueprint, request, jsonify
from flasgger import Swagger

from .models import Media
from .extentions import app
from utils.utils import create_file_url, file_manage, allowed_file

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
        name: data
        type: string
        required: true
        description: Les informations JSON pour le média (nom et description)
    responses:
      201:
        description: Nouveau fichier ajouté
      409:
        description: Un fichier avec ce nom ou cette URL existe déjà
    """

    #  Valeur initiale de l'url d'un fichier
    file_url = ""

    # Récupère le fichier envoyé via 'form-data' sous la clé 'file'
    file = request.files['file']
    # print(f'file: {file}')

    # Récupère les données supplémentaires envoyées sous la clé 'data' et les convertit en JSON
    data_json = request.form['data']
    # print(f'data_json: {data_json}')
    data = json.loads(data_json)
    # print(f'data: {data}')

    # Redéfinie l'url du fichier a enregistrer Génère l'URL où le fichier sera stocké
    file_url = create_file_url(file)
    # print(f'file_url: {file_url}')

    # Si un fichier avec le même nom existe, retourne un message d'erreur avec un code 409
    media = Media.get_media_by_name(name=data.get('name'))
    url_media = Media.get_media_by_url(url=file_url)
    # print(f'url_media: {url_media}')

    # Si un fichier avec le même nom ou avec la même URL existe, retourne un message d'erreur avec un code 409
    if media is not None:
        return jsonify({"msg": "File with this name is already exist"}), 409
    elif url_media is not None:
        return jsonify({"msg": "File with this url is already exist"}), 409
    else:
      # Sinon, crée un nouvel objet Media avec les informations fournies
        new_media = Media(
            name=data.get('name').lower(),
            description=data.get('description').lower(),
            media_url=file_url
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
              description: Message de succès
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
                  description:
                    type: string
                    description: Description du média
                  media_url:
                    type: string
                    description: URL du média
    """
    # Récupère tous les objets Media de la base de données
    medias = Media.query.all()

    # Sérialise les objets Media en JSON
    result = Media_schema().dump(medias, many=True)

    # Retourne la liste des médias avec un message de succès
    return jsonify({"msg": "All medias", "result": result}), 200


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
                description:
                  type: string
                  description: Description du média
                media_url:
                  type: string
                  description: URL du média
      404:
        description: Média non trouvé
    """

    # Récupère l'objet Media correspondant à l'ID donné
    media = Media.query.get(id)

    # Si le média n'existe pas, retourne un message d'erreur avec un code 404
    if media is None:
        return jsonify({"msg": "This media doesn't exist"}), 404

    # Sérialise l'objet Media en JSON
    result = Media_schema().dump(media)

    # Retourne les détails du média avec un code de succès 200
    return jsonify({"result": result}), 200


@media_bp.delete("/delete/<int:id>")
def delete_by_id(id):
    """
    Supprime un média par son ID
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
        description: Média non trouvé / File doesn't exit in the specify directory
    """

    # Cette fonction Supprime un fichier média par son ID et déplace son fichier associé dans un dossier de suppression supp_folder

    # Récupère l'objet Media correspondant à l'ID donné
    media = Media.query.get(id)

    # Si le média n'existe pas, retourne un message d'erreur avec un code 404
    if media is None:
        return jsonify({"msg": "This media doesn't exist"}), 404

    # Vérifie si le dossier de suppression existe, sinon il est créé
    if not os.path.exists(app.config['SUPP_FOLDER']):
        os.makedirs(app.config['SUPP_FOLDER'])

    # Vérifie si le fichier a supprimer existe, sinon il est créé
    if os.path.exists(media.media_url):

        lg.error(os.path.exists(app.config['SUPP_FOLDER']))

        # Déplace le fichier média vers le dossier de suppression (supp_folder)
        shutil.move(media.media_url, app.config['SUPP_FOLDER'])
        
        # Supprime l'enregistrement du média de la base de données
        Media.delete_by_id(media)
        
        # Supprime le fichier média
        # os.remove(media.media_url)
        
        lg.warning(media.media_url)

        # Retourne un message de succès après suppression
        return jsonify({"msg": "Done"})

    else:
      
        # Dans le cas ou le fichier a supprimer n'existe pas. supprimer le fichier de la base de données
        Media.delete_by_id(media)
        
        return jsonify({"msg": "File doesn't exit in the specify directory"}), 404