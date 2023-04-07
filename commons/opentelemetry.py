from functools import wraps
from collections.abc import Callable
from typing import ParamSpec, TypeVar

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


P = ParamSpec("P")
R = TypeVar("R")


def traced(func: Callable[P, R]) -> Callable[P, R]:
    """Wrap a function with open telemetry tracing"""

    @wraps(func)
    def with_tracing(*args: P.args, **kwargs: P.kwargs) -> R:
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(func.__name__):
            print("here")
            return func(*args, **kwargs)

    return with_tracing


P = ParamSpec("P")
R = TypeVar("R")


def super_tracing(func: Callable[P, R]) -> Callable[P, R]:
    """Wrap a function with open telemetry tracing"""
    tracer = trace.get_tracer(__name__)

    @wraps(func)
    def with_tracing(*args: P.args, **kwargs: P.kwargs) -> R:
        deep_func = func(*args, **kwargs)
        with tracer.start_as_current_span(func.__name__):
            print("here")
            print(deep_func)
            return deep_func()

    return with_tracing
