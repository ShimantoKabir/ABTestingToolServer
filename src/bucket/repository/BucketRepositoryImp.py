from src.bucket.repository.BucketRepository import BucketRepository
from src.bucket.model.Bucket import Bucket
from db import DBSessionDep
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

class BucketRepositoryImp(BucketRepository):
  def __init__(self, db: DBSessionDep):
    self.db = db

  def get(self, experimentId: int, endUserId: int) -> Bucket | None:
    return self.db.exec(
      select(Bucket)
      .where(Bucket.expId == experimentId)
      .where(Bucket.endUserId == endUserId)
    ).first()

  def add(self, bucket: Bucket) -> Bucket:
    try:
      self.db.add(bucket)
      self.db.commit()
      self.db.refresh(bucket)
      return bucket
    except IntegrityError:
      # If we hit a Unique Constraint error (Duplicate), 
      # it means another request just saved it.
      # We rollback the failed transaction and return the existing one.
      self.db.rollback()
      existing = self.get(bucket.expId, bucket.endUserId)
      return existing