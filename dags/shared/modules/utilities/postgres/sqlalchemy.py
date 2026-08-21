from typing import TypeVar

from sqlalchemy.orm import InstrumentedAttribute

T = TypeVar("T")

def field(attribute: T) -> InstrumentedAttribute[T]:
    return attribute