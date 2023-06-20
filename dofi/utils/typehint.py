from typing import TypeVar

from pydantic import BaseModel

SchemasType = TypeVar("SchemasType", bound=BaseModel)
