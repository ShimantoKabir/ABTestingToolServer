from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from src.experiment.model.ExperimentType import ExperimentType
from src.experiment.model.ExperimentStatus import ExperimentStatus
from src.experiment.model.TriggerType import TriggerType
from src.experiment.model.ConditionType import ConditionType

@dataclass
class ExperimentResponseDto:
  id: int
  title: str
  projectId: int
  type: ExperimentType
  status: ExperimentStatus
  url: Optional[str]
  description: Optional[str]
  triggerType: TriggerType
  conditionType: ConditionType
  js: Optional[str]
  css: Optional[str]
  createdAt: Optional[datetime]
  updatedAt: Optional[datetime]