from dataclasses import dataclass
from pydantic import Field
from typing import Optional

@dataclass
class PaginationRequestDto:
  orgId: int
  rows: int = Field(..., gt=0)
  page: int = Field(..., gt=0)
  total: Optional[int] = None
  projectId: Optional[int] = None

  
  

