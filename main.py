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

# creating db session
def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

model.Base.metadata.create_all(bind=engine)


app = FastAPI()


# @app.post("/")
# async def create_item(item: Item):
#     with redis.Redis() as redis_client:
#         redis_client.lpush("queue", 1)
#     print(item.job_id)
#     return item.job_id


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
    
    # resultList = list(dict.values())
    # print(resultList)


# import os
# import redis

# # Establish a connection to Redis
# r = redis.Redis(host='localhost', port=6379, db=0)

# # Specify the name of the Redis queue to read from
# queue_name = 'file_paths_queue'

# # Create a loop to continuously read messages from the Redis queue
# while True:
#     # Read a message from the Redis queue
#     message = r.brpop(queue_name)

#     # If the queue is empty, break the loop
#     if message is None:
#         break

#     # Get the path to the file from the message content
#     file_path = message[1].decode('utf-8')

#     # Read the contents of the file
#     with open(file_path, 'r') as f:
#         contents = f.read()

#     # Process the contents of the file as needed
#     # ...

