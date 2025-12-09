from dataclasses import dataclass
from typing import List, Optional
from pydantic import constr
from src.experiment.model.ExperimentType import ExperimentType
from src.experiment.model.ExperimentStatus import ExperimentStatus
from src.experiment.model.TriggerType import TriggerType
from src.experiment.model.ConditionType import ConditionType

@dataclass
class ExperimentCreateRequestDto:
  projectId: int
  title: constr(min_length=1) # type: ignore
  url: Optional[str] = None
  description: Optional[str] = None
  
