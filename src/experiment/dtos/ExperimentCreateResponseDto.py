from dataclasses import dataclass
from src.experiment.model.ExperimentStatus import ExperimentStatus

@dataclass
class ExperimentCreateResponseDto:
  id: int
  title: str
  status: ExperimentStatus