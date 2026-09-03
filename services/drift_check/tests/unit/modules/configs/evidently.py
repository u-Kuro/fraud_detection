from services.drift_check.src.modules.configs.evidently import EvidentlyConfig

def test_evidently_config_data_drift_key():
    assert EvidentlyConfig.data_drift_key == "data_drift"

def test_evidently_config_concept_drift_key():
    assert EvidentlyConfig.concept_drift_key == "concept_drift"

def test_evidently_config_drifted_key():
    assert EvidentlyConfig.drifted_key == "drifted"

def test_evidently_config_instantiation():
    config = EvidentlyConfig()
    assert config.data_drift_key == "data_drift"
    assert config.concept_drift_key == "concept_drift"
    assert config.drifted_key == "drifted"
