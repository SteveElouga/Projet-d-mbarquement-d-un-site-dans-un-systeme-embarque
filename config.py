import os


SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG")
SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL').replace("postgres://", "postgresql://")
SQLALCHEMY_DEBUG = os.getenv('SQLALCHEMY_DEBUG')
SWAGGER = {
    'title': os.getenv("SWAGGER_TITLE"),
    # Version de l'interface utilisateur Swagger UI
    'uiversion': int(os.getenv('SWAGGER_UIVERSION', 3)),
    'description': os.getenv("SWAGGER_DESCRIPTION"),
    'version': os.getenv('SWAGGER_VERSION'),
    'termsOfService': os.getenv('SWAGGER_TERMS_OF_SERVICE'),
    'contact': {
        'name': "Steve Ddider",
        'responsibleOrganization': os.getenv('SWAGGER_ORGANIZATION'),
        'responsibleDeveloper': os.getenv('SWAGGER_DEVELOPER'),
        'email': os.getenv('SWAGGER_EMAIL'),
        'url': os.getenv('SWAGGER_URL'),
    },
    'license': {
        'name': os.getenv("SWAGGER_LICENSE_NAME"),
        'url': os.getenv('SWAGGER_LICENSE_URL'),
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

