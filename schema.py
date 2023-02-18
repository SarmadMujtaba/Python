from datetime import date
from pydantic import BaseModel

class Job(BaseModel):
    job_id: str

    class Config:
        orm_mode = True

class User(BaseModel):
    user_id = str

    class Config:
        orm_mode = True