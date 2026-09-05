def test_health_path():
    # noinspection unused-imports
    import services.fraud_detection.src.controllers.routes.probes
    from services.fraud_detection.src.controllers.routes.probes import app
    assert any(route.path == "/health" for route in app.routes)

def test_ready_path():
    # noinspection unused-imports
    import services.fraud_detection.src.controllers.routes.probes
    from services.fraud_detection.src.controllers.routes.probes import app
    assert any(route.path == "/ready" for route in app.routes)