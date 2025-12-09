from dataclasses import dataclass
from typing import Optional
from pydantic import constr

@dataclass
class VariationCreateRequestDto:
  title: constr(min_length=1) # type: ignore
  js: Optional[str] = None
  css: Optional[str] = None