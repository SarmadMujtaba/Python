from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer

from database import Base

class Queue(Base):
    __tablename__ = "queue"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100))
    user_id = Column(String(100))

class Skills(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100))
    skill = Column(String(100))
 