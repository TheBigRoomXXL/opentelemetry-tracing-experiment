from models.book import Book

endpoint = "/books/"


def test_read_all_books(http_client, db):
    response = http_client.get(endpoint)
    assert response.status_code == 200

    books_db = db.session.execute(db.select(Book)).all()
    assert len(response.json) == len(books_db)


def test_add_book(http_client, db):
    data = [{"title": "Test-Driven Development by Example"}]
    response = http_client.post(endpoint, json=data)
    assert response.status_code == 201

    book_resp = response.json[0]
    assert book_resp["title"] == data[0]["title"]

    books_db = db.session.execute(db.select(Book)).all()
    assert len(books_db) == 1


def test_add_book_without_data(http_client, db):
    data = None
    response = http_client.post(endpoint, json=data)
    assert response.status_code == 422

    error = response.json
    print(error)
    assert error["errors"]["json"]["_schema"] == ["Invalid input type."]

    books_db = db.session.execute(db.select(Book)).all()
    assert len(books_db) == 0


def test_get_a_book(http_client, book):
    response = http_client.get(f"{endpoint}{book.id}")
    assert response.status_code == 200

    book_resp = response.json
    assert book_resp["id"] == book.id
    assert book_resp["title"] == book.title


def test_patch_book(http_client, db, book):
    data = {"title": "Unit Testing Principles, Practices, and Patterns"}
    response = http_client.patch(f"{endpoint}{book.id}", json=data)
    assert response.status_code == 200

    book_resp = response.json
    assert book_resp["title"] == data["title"]

    book_db = db.session.get(Book, book.id)
    assert book_db.title == data["title"]


def test_delete_book(http_client, db, book):
    response = http_client.delete(f"{endpoint}{book.id}")
    assert response.status_code == 204

    response = http_client.get(f"{endpoint}{book.id}")
    assert response.status_code == 404

    books_db = db.session.execute(db.select(Book)).all()
    assert len(books_db) == 0
