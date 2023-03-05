import redis
from fastapi import Request, FastAPI, Depends
# import time
import main
from sqlalchemy.orm import Session


redis_client = redis.Redis(host='localhost', port=6379, db=0)
queue_name = 'users'

async def shortlist_worker(db:Session=Depends(main.get_database_session)):
    print("worker")

    while True:
        user = redis_client.rpop(queue_name)
        
        if user is None:
            return
        print(user)
        # time.sleep(3)
        # print(len(user))
        
       


