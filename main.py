from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Request, FastAPI
import redis 

class user(BaseModel):
    user_id: str
   

class Item(BaseModel):
    job_id: str


app = FastAPI()


@app.post("/")
async def create_item(item: Item):
    with redis.Redis() as redis_client:
        redis_client.lpush("queue", 1)
    print(item.job_id)
    return item.job_id


@app.post("/{job_id}")
async def read_item(job_id, request: Request):
    print(job_id)
    dict = await request.json()
    print(dict[0])
