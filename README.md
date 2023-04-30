# OpenTelemetry instrumentation for Marshmallow

![Python](https://img.shields.io/badge/Python-blue?logo=python&logoColor=white)
![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-darkslateblue?logo=opentelemetry&logoColor=white)

Marshmallow is one of python most popular library when it comes to deserialization,
validation and serialization. As such it is an important part of the workflow in many
web framework.

This project aim at providing observability for those workflow with OpenTelemetry
tracing (no metric planned for now). If this project succeed, the resulting library will
be published to the [OpenTelemetry Python Contribution](https://github.com/open-telemetry/opentelemetry-python-contrib)

This repos IS NOT a library to instrument marshmallow, only a collection of experiment
on a small API.
