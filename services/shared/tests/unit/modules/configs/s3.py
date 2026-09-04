from services.shared.src.modules.configs.s3 import S3Config

def test_s3_config_model_drift_path_is_string():
    assert isinstance(S3Config.model_drift_path, str)

def test_s3_config_transaction_inferences_archive_path_is_string():
    assert isinstance(S3Config.transaction_inferences_archive_path, str)
