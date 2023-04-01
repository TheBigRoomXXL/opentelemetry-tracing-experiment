import pytest

from app import create_app
from commons import db as _db
from models.book import Book


@pytest.fixture(autouse=True)
def app():
    return create_app(testing=True)


@pytest.fixture(autouse=True)
def db(app):

    with app.app_context():
        _db.create_all()

    yield _db

    _db.session.close()
    _db.drop_all()


@pytest.fixture()
def http_client(app):
    return app.test_client()


@pytest.fixture
def book(db) -> Book:
    book = Book(name="Test-Driven Development with Python: Obey the Testing Goat!")
    db.session.add(book)
    db.session.commit()
    return book
