from dataclasses import dataclass

@dataclass(frozen=True)
class MLFlowConfig:
    challenger_alias: str = "challenger"
