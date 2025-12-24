from abc import ABC, abstractmethod
from src.menutemplate.model.MenuTemplate import MenuTemplate

class MenuTemplateRepository(ABC):
  @abstractmethod
  def getMenuTemplateById(self, id: int) -> MenuTemplate:
    pass

  @abstractmethod
  def add(self, role: MenuTemplate) -> MenuTemplate:
    pass

  @abstractmethod
  def getAllMenuTemplate(self, rows: int, page: int, orgId: int) -> list[MenuTemplate]:
    pass

  @abstractmethod
  def countAllMenuTemplate(self, orgId: int) -> int:
    pass

  @abstractmethod
  def getByUserIdAndOrgId(self, userId: int, orgId: int) -> MenuTemplate:
    pass