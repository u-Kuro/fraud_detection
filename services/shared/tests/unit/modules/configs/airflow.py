from services.shared.src.modules.configs.airflow import AirflowConfig

class TestAirflowConfig:
    def test_values(self):
        assert isinstance(AirflowConfig.xcom_file_path, str)