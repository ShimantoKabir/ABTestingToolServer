from dataclasses import dataclass
from typing import Optional

@dataclass
class DecisionRequestDto:
  url: str
  endUserId: Optional[int] = None