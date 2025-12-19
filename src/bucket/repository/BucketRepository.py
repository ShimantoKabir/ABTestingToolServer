from abc import ABC, abstractmethod
from src.bucket.model.Bucket import Bucket

class BucketRepository(ABC):
  
  @abstractmethod
  def get(self, experimentId: int, endUserId: int) -> Bucket | None:
    pass

  @abstractmethod
  def add(self, bucket: Bucket) -> Bucket:
    pass