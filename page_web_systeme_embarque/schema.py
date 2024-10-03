from marshmallow import Schema, fields


class Media_schema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()
    media_url = fields.String()
    created_at = fields.DateTime(format="%d/%m/%Y")
