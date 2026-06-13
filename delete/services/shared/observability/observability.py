import logging

from fastapi import FastAPI
from opentelemetry import trace as otel_trace, metrics as otel_metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider, TraceBasedExemplarFilter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import (
    Resource,
    SERVICE_NAME,
    SERVICE_VERSION,
    DEPLOYMENT_ENVIRONMENT,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from services.shared.schemas import OtelEnvironment
from sqlalchemy.engine.base import Engine


class Observability:
    def __init__(self, config: OtelEnvironment):
        self.config = config
        self.initialized = False

    def init(self) -> "Observability":
        if not self.config.OTEL_ENABLED:
            return self

        if self.initialized:
            return self
        else:
            self.initialized = True

        resource = Resource.create(
            {
                SERVICE_NAME: self.config.OTEL_SERVICE_NAME,
                SERVICE_VERSION: self.config.OTEL_SERVICE_VERSION,
                DEPLOYMENT_ENVIRONMENT: self.config.OTEL_DEPLOYMENT_ENVIRONMENT,
            }
        )

        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(
                OTLPLogExporter(endpoint=self.config.OTEL_URL, insecure=True)
            )
        )
        set_logger_provider(logger_provider)
        otel_handler = LoggingHandler(logger_provider=logger_provider)
        otel_handler.setLevel(logging.WARNING)
        root_logger = logging.getLogger()
        root_logger.addHandler(otel_handler)
        root_logger.critical()

        tracer_provider = TracerProvider(
            resource=resource,
            sampler=ParentBased(TraceIdRatioBased(0.1)),
        )
        tracer_provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=self.config.OTEL_URL, insecure=True)
            )
        )
        otel_trace.set_tracer_provider(tracer_provider)

        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[
                PeriodicExportingMetricReader(
                    exporter=OTLPMetricExporter(
                        endpoint=self.config.OTEL_URL,
                        insecure=True,
                    ),
                    export_interval_millis=self.config.OTEL_METRIC_EXPORT_INTERVAL_MS,
                )
            ],
            exemplar_filter=TraceBasedExemplarFilter(),
        )
        otel_metrics.set_meter_provider(meter_provider)

        BotocoreInstrumentor().instrument()

        return self

    def observe_sqlalchemy_engine(self, engine: Engine) -> "Observability":
        if not self.initialized:
            self.init()

        SQLAlchemyInstrumentor().instrument(engine=engine)

        return self

    def observe_fastapi_application(self, app: FastAPI) -> "Observability":
        if not self.initialized:
            self.init()

        FastAPIInstrumentor.instrument_app(app=app)

        return self
