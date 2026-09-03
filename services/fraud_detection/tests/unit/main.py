def get_route_paths(app):
    return {r.path for r in app.routes if hasattr(r, "path")}

def test_app_is_fastapi_instance():
    from fastapi import FastAPI
    from services.fraud_detection.src.main import app
    assert isinstance(app, FastAPI)

def test_app_has_predict_router():
    from services.fraud_detection.src.main import app
    # include_router wraps the router in _IncludedRouter; find via original_router
    included_routers = [r for r in app.routes if hasattr(r, "original_router")]
    prefixes = [r.original_router.prefix for r in included_routers]
    assert "/predict" in prefixes

def test_app_title():
    from services.fraud_detection.src.main import app
    assert "Fraud Detection" in app.title
