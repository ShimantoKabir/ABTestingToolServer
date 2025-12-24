from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, func
from src.db.links.UserOrgLink import UserOrgLink
from src.db.links.UserProjectLink import UserProjectLink

class User(SQLModel, table=True):

  __tablename__ = "userinfo"

  id: int = Field(default=None, primary_key=True)
  email: str = Field(index=True)
  password: str 
  otp: str = Field(default=None, nullable=True)
  verified: bool = Field(default=False , nullable=False)
  orgs: list["Organization"] = Relationship(back_populates="users", link_model=UserOrgLink) # type: ignore
  firstName: str = Field(default=None, nullable=True)
  lastName: str = Field(default=None, nullable=True)
  contactNumber: str = Field(default=None, nullable=True)
  projects: list["Project"] = Relationship(back_populates="users", link_model=UserProjectLink) # type: ignore
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
    
