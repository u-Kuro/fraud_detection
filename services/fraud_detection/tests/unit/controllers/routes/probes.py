def get_route_paths(app):
    # Filter out Mount/middleware objects that do not have a path attribute
    return {r.path for r in app.routes if hasattr(r, "path")}

def test_health_route_registered(mocker):
    mocker.patch("services.fraud_detection.src.repositories.mlflow.models.mlflow")
    # probes.py registers routes by decorating the app; import it to trigger registration
    import services.fraud_detection.src.controllers.routes.probes  # noqa: F401
    from services.fraud_detection.src.main import app
    assert "/health" in get_route_paths(app)

def test_ready_route_registered(mocker):
    mocker.patch("services.fraud_detection.src.repositories.mlflow.models.mlflow")
    import services.fraud_detection.src.controllers.routes.probes  # noqa: F401
    from services.fraud_detection.src.main import app
    assert "/ready" in get_route_paths(app)
