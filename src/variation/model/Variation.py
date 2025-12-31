from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Text, Column, DateTime, func
from typing import Optional
from datetime import datetime

class Variation(SQLModel, table=True):
  id: int = Field(default=None, primary_key=True)
  js: str = Field(default=None, nullable=True, sa_type=Text)
  css: str = Field(default=None, nullable=True, sa_type=Text)
  title: str = Field(default=None, nullable=True)
  traffic: int = Field(default=None, nullable=True)
  isControl: bool = Field(default=False, nullable=False)
  experiment: Optional["Experiment"] = Relationship(back_populates="variations") # type: ignore
  experimentId: Optional[int] = Field(default=None, foreign_key="experiment.id")
  createdAt: Optional[datetime] = Field(
    sa_column=Column(
      DateTime(timezone=True), server_default=func.now(), nullable=True
    )
  )
  updatedAt: Optional[datetime] = Field(
    sa_column=Column(
      DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
  )