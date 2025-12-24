from src.db.links.UserOrgLink import UserOrgLink
from src.menutemplate.repository.MenuTemplateRepository import MenuTemplateRepository
from src.menutemplate.model.MenuTemplate import MenuTemplate
from db import DBSessionDep
from fastapi import status, HTTPException
from sqlmodel import select
from sqlalchemy import func

class MenuTemplateRepositoryImp(MenuTemplateRepository):
  def __init__(self, db: DBSessionDep):
    self.db = db

  def getMenuTemplateById(self, id: int) -> MenuTemplate:
    mt = self.db.get(MenuTemplate,id)

    if not mt:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu template not found")
    
    return mt

  def add(self, mt: MenuTemplate) -> MenuTemplate:    
    self.db.add(mt)
    self.db.commit()
    self.db.refresh(mt)

    return mt
  
  def getAllMenuTemplate(self, rows: int, page: int, orgId: int)->list[MenuTemplate]:
    offset: int = (page - 1) * rows
    return self.db.exec(
      select(MenuTemplate)
      .where(MenuTemplate.orgId == orgId)
      .offset(offset).limit(rows)
    ).all()
  
  def countAllMenuTemplate(self, orgId: int) -> int:
    return self.db.exec(
      select(func.count(MenuTemplate.id))
      .where(MenuTemplate.orgId == orgId)
    ).one()
  
  def getByUserIdAndOrgId(self, userId: int, orgId: int) -> MenuTemplate:
    # SQL: SELECT * FROM menutemplate 
    #      JOIN userorglink ON menutemplate.id = userorglink.menuTemplateId
    #      WHERE userorglink.userId = :userId AND userorglink.orgId = :orgId
    
    statement = (
      select(MenuTemplate)
      .join(UserOrgLink, MenuTemplate.id == UserOrgLink.menuTemplateId)
      .where(UserOrgLink.userId == userId)
      .where(UserOrgLink.orgId == orgId)
    )
    
    result = self.db.exec(statement).first()

    if not result:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="No menu template found for this user and organization!"
      )
      
    return result



  