import inspect
import threading
import time
from _thread import LockType
from functools import wraps
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.trace import SpanKind, StatusCode

# ── Module-level caches, populated lazily on first use ──────────────────────
meters: dict[str, Any] = {}
tracers: dict[str, Any] = {}
instruments: dict[str, Any] = {}
lock: LockType = threading.Lock()  # guards all three caches against duplicate creation

def get_meter(module_name: str):
    if module_name not in meters:            # fast path
        with lock:
            if module_name not in meters:    # double-checked
                meters[module_name] = metrics.get_meter(module_name)
    return meters[module_name]

def get_tracer(module_name: str):
    if module_name not in tracers:
        with lock:
            if module_name not in tracers:
                tracers[module_name] = trace.get_tracer(module_name)
    return tracers[module_name]

def get_instruments(function_key: str, module_name: str, display_name: str) -> dict:
    if function_key not in instruments:
        with lock:
            if function_key not in instruments:
                meter = get_meter(module_name)
                instruments[function_key] = {
                    # RED — Duration  (latency percentiles; exemplars auto-attached when
                    #                  inside an active span → links to Tempo in Grafana)
                    "duration": meter.create_histogram(
                        name=f"{function_key}.duration",
                        description=f"Duration of {display_name} executions",
                        unit="s",
                    ),
                    # RED — Rate  (rate() in PromQL gives requests/sec)
                    "calls": meter.create_counter(
                        name=f"{function_key}.calls",
                        description=f"Total calls to {display_name}",
                        unit="{call}",
                    ),
                    # RED — Errors  (rate() gives error rate; error.type label for breakdown)
                    "errors": meter.create_counter(
                        name=f"{function_key}.errors",
                        description=f"Total errors raised by {display_name}",
                        unit="{error}",
                    ),
                }
    return instruments[function_key]

def static_span_attributes(function) -> dict:
    """
    Compute OTel semantic code.* span attributes once at decoration time,
    not on every call. filepath/line_number are best-effort.
    """
    attributes: dict[str, Any] = {
        "code.function": function.__name__,
        # code.namespace = enclosing class for methods, module for plain functions
        "code.namespace": (
            function.__qualname__.rsplit(".", 1)[0]
            if "." in function.__qualname__
            else function.__module__
        ),
    }
    try:
        attributes["code.filepath"] = inspect.getfile(function)
        _, line_number = inspect.getsourcelines(function)
        attributes["code.line_number"] = line_number
    except (TypeError, OSError):
        pass
    return attributes

def observe(function):
    """
    Decorator that instruments sync and async functions with LGTM-ready telemetry.

    Per invocation
    ──────────────
    Tracing  → INTERNAL span with semantic code.* attributes, StatusCode,
                and a span exception event (type + stacktrace, escaped=True)

    Metrics  → duration histogram  — p50/p95/p99; histogram exemplars carry
                                      trace_id/span_id → metric→trace links in Grafana
                calls counter      — RED Rate:  rate(calls[1m])
                errors counter     — RED Error: rate(errors[1m])
                                      labeled with error.type for breakdown by exception

    Prerequisite for metric→trace exemplars
    ────────────────────────────────────────
    1. MeterProvider must be configured with TraceBasedExemplarFilter (see observability.py)
    2. Prometheus exporter must have enable_open_metrics: true  (see otelcol-config.yaml)
    3. Prometheus must be started with --enable-feature=exemplar-storage
       (or feature_flags: [exemplar-storage] in prometheus.yml)
    """
    qualified_name = function.__qualname__
    module = function.__module__
    instrument_key = f"{module}.{qualified_name}"
    span_attributes = static_span_attributes(function)  # computed once

    if inspect.iscoroutinefunction(function):
        @wraps(function)
        async def async_wrapper(*args, **kwargs):
            inst = get_instruments(instrument_key, module, qualified_name)
            labels = {"function": qualified_name, "module": module}
            inst["calls"].add(1, attributes=labels)
            start_time = time.perf_counter()

            with get_tracer(module).start_as_current_span(
                qualified_name, kind=SpanKind.INTERNAL, attributes=span_attributes
            ) as span:
                try:
                    result = await function(*args, **kwargs)
                    span.set_status(StatusCode.OK)
                    return result
                except Exception as exception:
                    span.set_status(StatusCode.ERROR, str(exception))
                    # escaped=True → marks that the exception propagated out of the span
                    span.record_exception(exception, escaped=True)
                    inst["errors"].add(
                        1,
                        attributes={**labels, "error.type": type(exception).__qualname__},
                    )
                    raise
                finally:
                    # Record inside the span so the SDK can attach exemplars automatically
                    inst["duration"].record(time.perf_counter() - start_time, attributes=labels)

        return async_wrapper

    @wraps(function)
    def sync_wrapper(*args, **kwargs):
        instrument = get_instruments(instrument_key, module, qualified_name)
        labels = {"function": qualified_name, "module": module}
        instrument["calls"].add(1, attributes=labels)
        start_time = time.perf_counter()

        with get_tracer(module).start_as_current_span(
            qualified_name, kind=SpanKind.INTERNAL, attributes=span_attributes
        ) as span:
            try:
                result = function(*args, **kwargs)
                span.set_status(StatusCode.OK)
                return result
            except Exception as exception:
                span.set_status(StatusCode.ERROR, str(exception))
                span.record_exception(exception, escaped=True)
                instrument["errors"].add(
                    1,
                    attributes={**labels, "error.type": type(exception).__qualname__},
                )
                raise
            finally:
                instrument["duration"].record(time.perf_counter() - start_time, attributes=labels)

    return sync_wrapper
