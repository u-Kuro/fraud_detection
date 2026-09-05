class TestPredictRouter:
    def test_prefix(self):
        from services.fraud_detection.src.controllers.routers.predict import router
        assert router.prefix == "/predict"

    def test_tags(self):
        from services.fraud_detection.src.controllers.routers.predict import router
        assert "predict" in router.tags