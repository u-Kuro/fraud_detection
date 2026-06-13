import logging

from opentelemetry import trace
from services.fraud_api.src.services.middleware.request_id_middleware import request_id_var

class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True

class TraceAndSpanIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        ctx = trace.get_current_span().get_span_context()
        record.trace_id = f"{ctx.trace_id:032x}" if ctx.trace_id else ""
        record.span_id = f"{ctx.span_id:016x}" if ctx.span_id else ""
        return True