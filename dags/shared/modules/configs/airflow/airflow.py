from dataclasses import dataclass

@dataclass(frozen=True)
class AirflowConfig:
    owner: str = "mle"
    environment_prefix: str = "AIRFLOW_VAR_"

@dataclass(frozen=True)
class DagIDs:
    check_training_need: str = "check_training_need"
    on_training_decision: str = "on_training_decision"
    on_promotion_decision: str = "on_promotion_decision"