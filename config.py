FLASK_KEY = "9697ec9d39ce502235557f7dad19e213"
FLASK_DEBUG = True
SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
SQLALCHEMY_DEBUG = True
UPLOAD_IMAGE_FOLDER = "images/"
UPLOAD_PDF_FOLDER = "pdf/"
UPLOAD_VIDEO_FOLDER = "video/"
UPLOAD_TEXT_FOLDER = "text/"
UPLOAD_MUSIC_FOLDER = "music/"
UPLOAD_ELSE_FOLDER = "else/"
CORBEILLE_FOLDER = "corbeille/"
SWAGGER = {
    'title': 'API de gestion des médias',
    'uiversion': 3,  # Version de l'interface utilisateur Swagger UI
    'description': 'Cette API permet de gérer les fichiers multimédias, de les ajouter, les récupérer et les supprimer.',
    'version': '1.0.0',
    'termsOfService': '/terms',
    'contact': {
               'responsibleOrganization': 'ENSD',
               'responsibleDeveloper': 'Elouga Nyobe Steve Didier',
               'email': 'nyobeelouga5@gmail.com',
               'url': 'http://elouganyobe.com',
    },
    'license': {
        'name': 'ENSPD',
        'url': 'https://opensource.org/licenses/ENSPD',
    },
    'specs': [
        {
            'endpoint': 'apispec_1',
            'route': '/apispec_1.json',
            'rule_filter': lambda rule: True,  # Inclut toutes les routes
            'model_filter': lambda tag: True,  # Inclut tous les modèles
        }
    ],
    'static_url_path': '/flasgger_static',  # Où les fichiers statiques sont servis
    'swagger_ui': True,  # Active l'interface Swagger UI
    'specs_route': '/'  # URL où Swagger sera disponible
}
