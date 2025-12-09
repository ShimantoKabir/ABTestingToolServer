from typing import Optional
from pydantic import model_validator, BaseModel, field_validator, HttpUrl, TypeAdapter, ValidationError
from src.experiment.model.ExperimentType import ExperimentType
from src.experiment.model.ExperimentStatus import ExperimentStatus
from src.experiment.model.TriggerType import TriggerType
from src.experiment.model.ConditionType import ConditionType

class ExperimentUpdateRequestDto(BaseModel):
  title: Optional[str] = None
  js: Optional[str] = None
  css: Optional[str] = None
  type: Optional[ExperimentType] = None
  status: Optional[ExperimentStatus] = None
  url: Optional[str] = None
  description: Optional[str] = None
  triggerType: Optional[TriggerType] = None
  conditionType: Optional[ConditionType] = None

  # 1. Validate URL format if provided
  @field_validator('url')
  def validate_url(cls, v):
    if v is not None:
      try:
        # We use Pydantic's TypeAdapter to validate the string as a HttpUrl
        TypeAdapter(HttpUrl).validate_python(v)
      except ValidationError:
        raise ValueError("Invalid URL format!")
    return v

  # 2. Existing validator to ensure at least one field is present
  @model_validator(mode='after')
  def check_at_least_one_field(self):
    # Check if all fields are None
    if not any(value is not None for value in self.__dict__.values()):
      raise ValueError("At least one field must be provided for update!")
    return self