from functools import wraps
from collections.abc import Callable
from typing import ParamSpec, TypeVar, Collection, Any
from copy import deepcopy
from logging import getLogger

from opentelemetry.trace import get_tracer
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

from marshmallow import Schema, decorators


P = ParamSpec("P")
R = TypeVar("R")


class MarshmallowInstrumentor(BaseInstrumentor):
    _LOG = getLogger(__name__)
    __version__ = "0.0.1"
    _instrumented_schemas = []
    _original_hooks = deepcopy(decorators.set_hook)
    tracer = get_tracer(__name__, __version__)

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["marshmallow"]

    def _instrument(self, *args, **kwargs) -> None:
        """Instrument marshmallow"""
        self.tracer_provider = kwargs.get("tracer_provider")
        self.tracer = get_tracer(__name__, self.__version__, self.tracer_provider)

        self.instrument_schema(Schema)
        self._instrument_decorators()

    def instrument_schema(self, schema: Schema):
        self._instrumented_schemas.append((schema, deepcopy(schema)))
        schema.load = self._traced(schema.load)
        schema.dump = self._traced(schema.dump)
        schema.validate = self._traced(schema.validate)

    def _instrument_decorators(self) -> Callable[P, R]:
        """Wrap user hooks with tracing"""

        @wraps(decorators.set_hook)
        def set_hook_with_tracing(
            fn: Callable[..., Any] | None, key: tuple[str, bool] | str, **kwargs: Any
        ) -> Callable[..., Any]:
            fn = self._traced(fn)
            return fn

        return set_hook_with_tracing

    def _uninstrument(self, *args, **kwargs) -> None:
        """Uninstrument the library"""
        for (schema, original_state) in self._instrumented_schemas:
            schema = original_state  # noqa: F841
        decorators.set_hook = self._original_hooks

    def _traced(self, func: Callable[P, R]) -> Callable[P, R]:
        """Wrap a Schema function with open telemetry tracing"""

        @wraps(func)
        def with_tracing(_self: Schema, *args: P.args, **kwargs: P.kwargs) -> R:
            with self.tracer.start_as_current_span(
                func.__name__, set_status_on_exception=False
            ) as span:
                span.set_attribute("schema", _self.__class__.__name__)
                span.set_attribute("schema.fields", str(list(_self.fields)))
                span.set_attribute("schema.many", _self.many)
                span.set_attribute("schema.partial", _self.partial)
                span.set_attribute("schema.unknown", _self.unknown)
                span.set_attribute("schema.ordered", _self.ordered)

                result = func(_self, *args, **kwargs)
                return result

        return with_tracing
