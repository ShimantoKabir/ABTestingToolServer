from abc import ABC, abstractmethod
from src.experiment.model.Experiment import Experiment

class ExperimentRepository(ABC):
  
  @abstractmethod
  def add(self, experiment: Experiment) -> Experiment:
    pass

  @abstractmethod
  def getById(self, id: int) -> Experiment:
    pass

  @abstractmethod
  def getAll(self, rows: int, page: int, projectId: int) -> list[Experiment]:
    pass

  @abstractmethod
  def countAll(self, projectId: int) -> int:
    pass

  @abstractmethod
  def edit(self, experiment: Experiment) -> Experiment:
    pass

  @abstractmethod
  def getAllActive(self, rows: int, page: int, projectId: int) -> list[Experiment]:
    pass