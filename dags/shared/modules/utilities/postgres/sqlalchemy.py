from sqlalchemy.orm import InstrumentedAttribute
from typing import TypeVar

T = TypeVar("T")

def field(attribute: T) -> InstrumentedAttribute[T]:
    return attribute