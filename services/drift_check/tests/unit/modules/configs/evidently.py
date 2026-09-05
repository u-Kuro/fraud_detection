from services.drift_check.src.modules.configs.evidently import EvidentlyConfig

class TestEvidentlyConfig:
    def test_values(self):
        assert isinstance(EvidentlyConfig.data_drift_key, str)
        assert isinstance(EvidentlyConfig.concept_drift_key, str)
        assert isinstance(EvidentlyConfig.drifted_key, str)