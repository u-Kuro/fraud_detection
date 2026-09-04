# TODO - 04/09/2026 - Continue here... redo all fraud_detection and train_model and dags

def get_route_paths(app):
    return {r.path for r in app.routes if hasattr(r, "path")}

def test_app_is_fastapi_instance():
    from fastapi import FastAPI
    from services.fraud_detection.src.main import app
    assert isinstance(app, FastAPI)

def test_app_has_predict_router():
    from services.fraud_detection.src.main import app

    paths = [route.path for route in app.routes if hasattr(route, "path")]
    assert any(path.startswith("/predict") for path in paths)

def test_app_title():
    from services.fraud_detection.src.main import app
    assert "Fraud Detection" in app.title
