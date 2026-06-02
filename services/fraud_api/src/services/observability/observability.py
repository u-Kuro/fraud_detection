import logging

from pythonjsonlogger import json

from services.fraud_api.src.modules.environment import environment
from services.fraud_api.src.services.observability.logging.filters import TraceAndSpanIdFilter, RequestIdFilter
from services.shared.observability import Observability as BaseObservability

class Observability(BaseObservability):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def init(self):
        super().init()
        console_handler = logging.StreamHandler()
        formatter = json.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(request_id)s %(trace_id)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
        )
        console_handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addFilter(RequestIdFilter())
        root_logger.addFilter(TraceAndSpanIdFilter())
        root_logger.addHandler(console_handler)

observability: Observability = Observability(environment)