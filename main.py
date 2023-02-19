from fastapi import FastAPI
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import Request, FastAPI, Depends
import redis 

from schema import DataSchema
from database import SessionLocal, engine
import model

# Redis Code
redis_client = redis.Redis(host='localhost', port=6379, db=0)
queue_name = 'users'

# Creating db session
def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

model.Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.post("/{job_id}")
async def read_item(job_id, request: Request, db:Session=Depends(get_database_session)):
    print(job_id)
    redultList = await request.json()
    print(len(redultList))
    
    # Adding record to database
    for x in redultList:
        print(x["user_id"])
        record = model.Queue()
        record.job_id = job_id
        record.user_id = x["user_id"]
        db.add(record)
        db.commit()
    
    # Adding users to queue
    for x in redultList:
        redis_client.lpush(queue_name, x["user_id"])
    
    