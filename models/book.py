from marshmallow import fields

from commons import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow.validate import Length


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hint = db.Column(db.String, nullable=True)
    title = db.Column(db.String, nullable=False)
    author_name = db.Column(db.String, nullable=True)
    publication_year = db.Column(db.Integer, nullable=True)
    ISBN = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)


class Bookshema(SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        include_relationships = True

    id = auto_field(dump_only=True)
    hint = fields.Str(load_only=True)
    description = auto_field(validate=Length(max=500))
