from dataclasses import dataclass
from typing import Optional

@dataclass
class VariationResponseDto:
  id: int
  experimentId: int
  title: str
  traffic: int
  js: Optional[str]
  css: Optional[str]