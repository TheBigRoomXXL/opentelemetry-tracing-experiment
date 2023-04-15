from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model


class MyDbModel(Model):
    """MyDbModel is used as the "model_class" of db (aka db.Model).
    Extend the SQLAlchemy functionalities throught this class."""

    def patch(self, update_dictionary: dict) -> None:
        """Partial update an object with a simple and clear syntax"""
        for col_name in self.__table__.columns.keys():
            if col_name in update_dictionary:
                setattr(self, col_name, update_dictionary[col_name])


db = SQLAlchemy(model_class=MyDbModel)
api = Api()
