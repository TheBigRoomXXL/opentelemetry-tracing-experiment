from flask_smorest import Api
from flask_smorest import Blueprint
from opentelemetry import trace

api = Api()


class InstrumentedBlueprint(Blueprint):
    tracer = trace.get_tracer(__name__)

    @tracer.start_as_current_span("processing_argument")
    def arguments(*args, **kwargs):
        print("here")
        return Blueprint.arguments(*args, **kwargs)
