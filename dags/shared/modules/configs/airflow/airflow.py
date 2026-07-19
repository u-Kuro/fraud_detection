from dataclasses import dataclass

@dataclass(frozen=True)
class AirflowConfig:
    owner: str = "mle"
    base_environment_prefix: str = "AIRFLOW_VAR_"
    mle_environment_prefix: str = "MLE"

    @classmethod
    def environment_prefix(cls) -> str:
        return f"{cls.base_environment_prefix}{cls.mle_environment_prefix}_"

@dataclass(frozen=True)
class DagIDs:
    model_lifecycle_orchestrator: str = "model_lifecycle_orchestrator"
    challenger_model_invalidation: str = "challenger_model_invalidation"
    training_approval_dispatch: str = "training_approval_dispatch"