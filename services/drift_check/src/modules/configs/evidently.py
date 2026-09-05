from dataclasses import dataclass

@dataclass(frozen=True)
class EvidentlyConfig:
    data_drift_key: str = "data_drift"
    concept_drift_key: str = "concept_drift"
    drifted_key: str = "drifted"