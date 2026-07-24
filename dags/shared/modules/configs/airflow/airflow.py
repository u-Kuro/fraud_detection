from dataclasses import dataclass

@dataclass(frozen=True)
class AirflowConfig:
    owner: str = "mle"

    kubeconfig_file_path: str = "/usr/local/airflow/dags/kubeconfig.yaml"

    base_environment_prefix: str = "AIRFLOW_VAR_"
    mle_environment_prefix: str = "MLE"

    @classmethod
    def environment_prefix(cls) -> str:
        return f"{cls.base_environment_prefix}{cls.mle_environment_prefix}_"

@dataclass(frozen=True)
class DagIDs:
    check_training_need: str = "check_training_eligibility"
    on_training_decision: str = "on_training_decision"
    on_promotion_decision: str = "on_promotion_decision"