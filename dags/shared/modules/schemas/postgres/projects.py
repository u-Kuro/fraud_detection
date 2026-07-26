from dataclasses import dataclass

@dataclass(frozen=True)
class ProjectsColumnKeys:
    id: str = "id"
    created_at: str = "created_at"
    name: str = "name"