def test_predict_router_path_prefix():
    from services.fraud_detection.src.controllers.routers.predict import router
    assert router.prefix == "/predict"

def test_predict_router_tags():
    from services.fraud_detection.src.controllers.routers.predict import router
    assert "predict" in router.tags
