from datetime import date
from pydantic import BaseModel


class DataSchema(BaseModel):
    user_id = str
    job_id = str

    class Config:
        orm_mode = True