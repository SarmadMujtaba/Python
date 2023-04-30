import redis
from fastapi import Request, FastAPI, Depends
import time
import main
import model
from sqlalchemy.orm import Session


redis_client = redis.Redis(host='redis', port=6379, db=0)
queue_name = 'users'

async def shortlist_worker(db:Session = next(main.get_database_session())):

    while True:
        skillList = []
        reqSkillList = []
        count = 0 

        user = redis_client.rpop(queue_name)

        if user is None:
            return

        # getting user's data
        data = db.query(model.Queue).filter(model.Queue.user_id == user).first()

        # getting job_id in which user has applied for and getting its required skills
        data2 = db.query(model.reqSkills).filter(model.reqSkills.job_id == data.job_id).all()
        for i in range(len(data2)):
            if data2[i].skill not in reqSkillList:
                reqSkillList.append(data2[i].skill)

        # lower casing required skills for comparison with user skills
        for i in range(len(reqSkillList)):
            reqSkillList[i] = reqSkillList[i].lower()
        print(reqSkillList)

        # getting all the skills of the user
        data3 = db.query(model.Skills).filter(model.Skills.user_id == user).all()
        for i in range(len(data3)):
            if data3[i].skill not in skillList:
                skillList.append(data3[i].skill)
        print(skillList)

        # matching required skills with user's skills
        for x in reqSkillList:
            if x in skillList:
                count += 1
        
        print(count)
        reqSkills = len(reqSkillList)

        # updating status in database 
        if count >= (int(0.7 * reqSkills)):
            print("Success")
            db.query(model.Queue).filter(model.Queue.user_id == user , model.Queue.job_id == data.job_id).update({model.Queue.status: 'success'}, synchronize_session=False)
            db.commit()
            count == 0
        else:
            print("Fail")
            db.query(model.Queue).filter(model.Queue.user_id == user , model.Queue.job_id == data.job_id).update({model.Queue.status: 'fail'}, synchronize_session=False)
            db.commit()
            count == 0










       


