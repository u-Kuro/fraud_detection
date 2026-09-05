from dataclasses import dataclass

@dataclass(frozen=True)
class MLflowConfig:
    challenger_alias: str = "challenger"
