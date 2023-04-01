from flask.views import MethodView
from flask_smorest import Blueprint

from opentelemetry import trace

from commons import db
from models.book import Book, Bookshema

tracer = trace.get_tracer(__name__)

blp = Blueprint(
    "books", "books", url_prefix="/books", description="Operations on books"
)


@blp.route("/")
class Books(MethodView):
    @blp.arguments(Bookshema(partial=True), location="query")
    @blp.response(200, Bookshema(many=True))
    def get(self, filters: dict) -> list:
        """List books"""
        return db.session.scalars(db.select(Book).filter_by(**filters)).all()

    @blp.arguments(Bookshema)
    @blp.response(201, Bookshema)
    def post(self, new_book) -> Book:
        """Add a new book"""
        book = Book(**new_book)
        db.session.add(book)
        db.session.commit()
        return book


@blp.route("/<book_id>")
class BooksById(MethodView):
    @blp.response(200, Bookshema)
    def get(self, book_id) -> Book:
        """Get book by ID"""
        book = db.get_or_404(Book, book_id)
        return book

    @blp.arguments(Bookshema)
    @blp.response(200, Bookshema)
    def patch(self, update_data, book_id) -> Book:
        """Patch existing book"""
        book = db.get_or_404(Book, book_id)
        book.patch(update_data)
        db.session.commit()
        return book

    @blp.response(204)
    def delete(self, book_id) -> None:
        """Delete book"""
        book = db.get_or_404(Book, book_id)
        db.session.delete(book)
        db.session.commit()
