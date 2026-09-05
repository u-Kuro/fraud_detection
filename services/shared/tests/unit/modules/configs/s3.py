from services.shared.src.modules.configs.s3 import S3Config

class TestS3Config:
    def test_values(self):
        assert isinstance(S3Config.model_drift_path, str)
        assert isinstance(S3Config.transaction_inferences_archive_path, str)