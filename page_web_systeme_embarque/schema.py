from marshmallow import Schema, fields


class Media_schema(Schema):
    id = fields.Integer()
    titre = fields.String()
    name = fields.String()
    description = fields.String()
    media_url = fields.String()
    type = fields.String()
    status = fields.String()
    created_at = fields.DateTime(format="%d/%m/%Y %H:%M:%S")
