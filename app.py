from flask import Flask

from commons import config, api, db
from commons.otel import register_opentelemetry
from ressources.book import blp


def create_app(testing: bool = False) -> Flask:
    _app = Flask(__name__)
    _app.config.from_object(config)

    api.init_app(_app)
    api.register_blueprint(blp)

    db.init_app(_app)
    with _app.app_context():
        db.drop_all()
        db.create_all()

    register_opentelemetry(_app, db)

    return _app


app = create_app()
