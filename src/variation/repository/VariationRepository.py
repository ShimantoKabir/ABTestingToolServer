from abc import ABC, abstractmethod
from src.variation.model.Variation import Variation

class VariationRepository(ABC):
  
  @abstractmethod
  def add(self, variation: Variation) -> Variation:
    pass

  @abstractmethod
  def getByExperimentId(self, experimentId: int) -> list[Variation]:
    pass
    
  @abstractmethod
  def saveAll(self, variations: list[Variation]) -> list[Variation]:
    pass

  @abstractmethod
  def getById(self, id: int) -> Variation:
    pass

  @abstractmethod
  def edit(self, variation: Variation) -> Variation:
    pass

  @abstractmethod
  def delete(self, variation: Variation):
    pass