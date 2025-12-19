from src.experiment.model.ExperimentStatus import ExperimentStatus
from src.experiment.repository.ExperimentRepository import ExperimentRepository
from src.experiment.model.Experiment import Experiment
from db import DBSessionDep
from fastapi import status, HTTPException
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload

class ExperimentRepositoryImp(ExperimentRepository):
  def __init__(self, db: DBSessionDep):
    self.db = db

  def add(self, experiment: Experiment) -> Experiment:
    self.db.add(experiment)
    self.db.commit()
    self.db.refresh(experiment)
    return experiment

  def getById(self, id: int) -> Experiment:
    experiment = self.db.get(Experiment, id)
    if not experiment:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")
    return experiment

  def getAll(self, rows: int, page: int, projectId: int) -> list[Experiment]:
    offset: int = (page - 1) * rows
    return self.db.exec(
      select(Experiment)
      .where(Experiment.projectId == projectId)
      .offset(offset).limit(rows)
    ).all()

  def countAll(self, projectId: int) -> int:
    return self.db.exec(
      select(func.count(Experiment.id))
      .where(Experiment.projectId == projectId)
    ).one()

  def edit(self, experiment: Experiment) -> Experiment:
    self.db.add(experiment)
    self.db.commit()
    self.db.refresh(experiment)
    return experiment
  
  def getAllActive(self, rows: int, page: int, projectId: int) -> list[Experiment]:
    offset: int = (page - 1) * rows
    return self.db.exec(
      select(Experiment)
      .where(Experiment.projectId == projectId)
      .where(Experiment.status == ExperimentStatus.ACTIVE)
      .options(
          selectinload(Experiment.conditions),
          selectinload(Experiment.variations),
          selectinload(Experiment.metrics)
      )
      .offset(offset).limit(rows)
    ).all()