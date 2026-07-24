from dataclasses import dataclass

@dataclass(frozen=True)
class ProjectsColumnKeys:
    id = "id"
    created_at = "created_at"
    name = "name"