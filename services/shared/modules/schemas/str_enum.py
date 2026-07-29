from enum import StrEnum
from typing import Self

class BaseStrEnum(StrEnum):
    @classmethod
    def to_set(
        cls,
        rename: dict[Self, str]
    ) -> set[str]:
        items = set(cls)
        items -= rename.keys()
        items |= set(rename.values())
        return items