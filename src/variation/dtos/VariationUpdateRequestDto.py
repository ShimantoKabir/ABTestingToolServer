from typing import Optional
from pydantic import BaseModel, model_validator, constr

class VariationUpdateRequestDto(BaseModel):
  title: Optional[str] = None
  js: Optional[str] = None
  css: Optional[str] = None

  @model_validator(mode='after')
  def check_at_least_one_field(self):
    if not any(value is not None for value in self.__dict__.values()):
      raise ValueError("At least one field (title, js, css) must be provided!")
    return self