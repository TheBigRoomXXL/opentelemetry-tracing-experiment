from commons import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)


class Bookshema(SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        include_relationships = True

    id = auto_field(dump_only=True)
