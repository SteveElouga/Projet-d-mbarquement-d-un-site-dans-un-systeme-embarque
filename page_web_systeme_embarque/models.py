from sqlalchemy import func
from .extentions import db, app

import logging as lg


class Media(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    titre = db.Column(db.String(50), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=True, index=True)
    status = db.Column(db.String(50), nullable=True, server_default="active")
    description = db.Column(db.String())
    media_url = db.Column(db.String(), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime(), server_default=func.now())

    def __repr__():
        return f"<Media {Media.name}>"

    @classmethod
    def get_media_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_media_by_url(cls, url):
        return cls.query.filter_by(media_url=url).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def delete_by_id(self):
        db.session.delete(self)
        db.session.commit()


def init_db():
    db.create_all()
    lg.warning('La base de donnees a ete initilisee!')
