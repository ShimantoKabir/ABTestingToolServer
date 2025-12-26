from abc import ABC, abstractmethod
from src.user.model.User import User

class UserRepository(ABC):
  @abstractmethod
  def getUserById(self, id: int) -> User:
    pass

  @abstractmethod
  def add(self, user: User) -> User:
    pass

  @abstractmethod
  def getUserByEmail(self, email: str) -> User:
    pass

  @abstractmethod
  def updateUser(self, user: User) -> User:
    pass

  @abstractmethod
  def getAllUser(self, rows: int, page: int, orgId: int) -> list[User]:
    pass

  @abstractmethod
  def countAllUser(self, orgId: int) -> int:
    pass

  @abstractmethod
  def getUserDetailsByOrgAndUser(self, userId: int, orgId: int):
    pass