from dataclasses import dataclass
from typing import List
from pydantic import BaseModel, field_validator

class VariationTrafficDto(BaseModel):
  variationId: int
  traffic: int

class TrafficAllocationRequestDto(BaseModel):
  allocations: List[VariationTrafficDto]

  @field_validator('allocations')
  def validate_total_traffic(cls, v):
    total = sum(item.traffic for item in v)
    if total != 100:
      raise ValueError(f"Total traffic allocation must equal 100%. Current total: {total}%!")
    return v