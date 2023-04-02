from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def register_opentelemetry(app: Flask, db: SQLAlchemy) -> None:
    resource = Resource(attributes={SERVICE_NAME: "book-api"})

    exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)

    processor = BatchSpanProcessor(exporter)

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

    FlaskInstrumentor.instrument_app(app, enable_commenter=True)
    with app.app_context():
        SQLAlchemyInstrumentor().instrument(engine=db.engine, enable_commenter=True)
