from .extentions import app, db, migrate
from . import models
from .media_read_write import media_bp, Swagger

db.init_app(app)
migrate.init_app(app, db)
swagger = Swagger(app)


app.register_blueprint(media_bp, url_prefix='/api')


@app.cli.command('init_db')
def init_db():
    models.init_db()
