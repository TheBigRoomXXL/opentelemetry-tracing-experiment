from functools import wraps
from collections.abc import Callable
from typing import ParamSpec, TypeVar, Collection, Any
from copy import deepcopy
from logging import getLogger

from marshmallow import Schema, decorators

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
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
    MarshmallowInstrumentor().instrument()
    with app.app_context():
        SQLAlchemyInstrumentor().instrument(engine=db.engine, enable_commenter=True)


P = ParamSpec("P")
R = TypeVar("R")


class MarshmallowInstrumentor(BaseInstrumentor):
    _LOG = getLogger(__name__)
    __version__ = "0.0.1"

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["marshmallow"]

    def traced(self, func: Callable[P, R]) -> Callable[P, R]:
        """Wrap a function with open telemetry tracing"""

        @wraps(func)
        def with_tracing(*args: P.args, **kwargs: P.kwargs) -> R:
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(
                func.__name__, set_status_on_exception=False
            ):
                result = func(*args, **kwargs)
                return result

        return with_tracing

    def _instrument(self) -> None:
        """Instrument marshmallow"""
        self._original_schema = deepcopy(Schema)
        if self._is_instrumented_by_opentelemetry:
            self._LOG.warning(
                "Attempting to instrument Marshmallow while already instrumented"
            )
            return None

        # tracer = trace.get_tracer(__name__, tracer_provider)
        Schema.load = self.traced(Schema.load)
        Schema.dump = self.traced(Schema.dump)
        Schema.validate = self.traced(Schema.validate)
        decorators.set_hook = self._inject_tracing_in_set_hook()

        self._is_instrumented_by_opentelemetry = True

    def _uninstrument(self, *args, **kwargs) -> None:
        """Uninstrument the library"""
        if not self._is_instrumented_by_opentelemetry:
            self._LOG.warning(
                "Attempting to uninstrument Marshmallow while not instrumented"
            )
            return None
        Schema = self._original_schema  # noqa: F841

    def _inject_tracing_in_set_hook(self) -> Callable[P, R]:
        """Wrap user hooks with tracing"""

        @wraps(decorators.set_hook)
        def set_hook_with_tracing(
            fn: Callable[..., Any] | None, key: tuple[str, bool] | str, **kwargs: Any
        ) -> Callable[..., Any]:
            fn = self.traced(fn)
            return fn

        return set_hook_with_tracing
