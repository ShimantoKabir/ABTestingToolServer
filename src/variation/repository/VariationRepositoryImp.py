from src.variation.repository.VariationRepository import VariationRepository
from src.variation.model.Variation import Variation
from db import DBSessionDep
from sqlmodel import select
from fastapi import status, HTTPException

class VariationRepositoryImp(VariationRepository):
  def __init__(self, db: DBSessionDep):
    self.db = db

  def add(self, variation: Variation) -> Variation:
    self.db.add(variation)
    self.db.commit()
    self.db.refresh(variation)
    return variation

  def getByExperimentId(self, experimentId: int) -> list[Variation]:
    return self.db.exec(
      select(Variation).where(Variation.experimentId == experimentId)
    ).all()

  def saveAll(self, variations: list[Variation]) -> list[Variation]:
    for v in variations:
      self.db.add(v)
    self.db.commit()
    for v in variations:
      self.db.refresh(v)
    return variations

  def getById(self, id: int) -> Variation:
    variation = self.db.get(Variation, id)
    if not variation:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variation not found")
    return variation

  def edit(self, variation: Variation) -> Variation:
    self.db.add(variation)
    self.db.commit()
    self.db.refresh(variation)
    return variation