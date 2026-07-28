from dataclasses import dataclass
from pathlib import Path, PurePath

@dataclass(frozen=True)
class ProjectConfig:
    root_path: PurePath = Path(__file__).parents[4]
