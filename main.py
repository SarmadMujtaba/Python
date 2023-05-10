from fastapi import FastAPI
from sqlalchemy.orm import Session
from fastapi import Request, FastAPI, Depends
import redis 
import fnmatch
import os
# import globals

import pandas as pd
from PyPDF2 import PdfReader
import spacy
from spacy.matcher import PhraseMatcher
from fastapi import FastAPI, HTTPException

from database import SessionLocal, engine
import model

# Redis Code
redis_client = redis.Redis(host='redis', port=6379, db=0)
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

# endpoint for extracting skills from resume when user uploads it.

@app.post("/extract")
async def read_item(request: Request, db:Session=Depends(get_database_session)):
    user_id = await request.json()
    file_name: str
    # print(user_id)

    # getting the matched file name (without docker '/home/sarmad/Desktop/FYP_Resumes')
    for file in os.listdir('/app/Resumes'):
        if fnmatch.fnmatch(file, user_id + '_*.pdf'):
            print(file)
            file_name = file

    # reading matched file (without docker '/home/sarmad/Desktop/FYP_Resumes/')
    reader = PdfReader('/app/Resumes/' + file_name)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    text = text.replace("  ", " ")
    text = text.lower()
    # print(text)

    # Skills Extraction using spacy
    nlp = spacy.load('en_core_web_sm')
    matcher = PhraseMatcher(nlp.vocab)
    nlp_text = nlp(text)
    
    # reading the csv files (without docker '/home/sarmad/Go_Practice/PythonService/skills.csv')
    data = pd.read_csv("/app/skills.csv") 
    data2 = pd.read_csv("/app/PhraseSkills.csv") 

    # extract values to lists
    phraseSkills = list(data2.columns.values)
    skills = list(data.columns.values)

    # print(skills)
    # print(phraseSkills)
    
    skillset = []
    
    # check for one-grams (example: python)
    for token in skills:
        if token in nlp_text.text:
            skillset.append(token)
    

    # check for bi-grams and tri-grams (example: machine learning)
    patterns = [nlp.make_doc(text) for text in phraseSkills]
    matcher.add("TerminologyList", None, *patterns)
    matches = matcher(nlp_text)
   
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        if span.text not in skillset:
            skillset.append(span.text)

    # Insert data in database
    for x in skillset:
        record = model.Skills()
        record.user_id = user_id
        record.skill = x
        db.add(record)
        db.commit()

    print(skillset)

    

#  end point for shortlisting jobs 
@app.post("/{job_id}")
async def read_item(job_id, request: Request, db:Session=Depends(get_database_session)):
    print(job_id)
    # globals.JOB = job_id
    # users = []
    resultList = await request.json()
    print(resultList)
    
    # Adding record to database
    for x in resultList["Users"]:
    #     print(x)
        record = model.Queue()
        record.job_id = job_id
        record.user_id = x
        record.status = "pending"
        db.add(record)
        db.commit()

    for x in resultList["RequiredSkills"]:
    #     print(x)
        record = model.reqSkills()
        record.job_id = job_id
        record.skill= x
        db.add(record)
        db.commit()
    
    # # Adding users to queue
    for x in resultList["Users"]:
        redis_client.lpush(queue_name, job_id + ":" + x)


    import worker
    await worker.shortlist_worker()



# endpoint for adding user's skills in to db (for users without uploading resume)
@app.post("/skills/{user_id}")
async def add_skill(user_id, request: Request, db:Session=Depends(get_database_session)):
    print(user_id)
    # users = []
    resultList = await request.json()
    print(resultList)
    
    # Adding record to database

    record = model.Skills()
    record.user_id = user_id
    record.skill = resultList
    db.add(record)
    db.commit()


@app.get("/status/{job_id}")
async def status(job_id, request: Request, db:Session=Depends(get_database_session)):

    list = db.query(model.Queue).filter(model.Queue.job_id == job_id).all()
    print(len(list))
    
    if len(list) == 0:
        raise HTTPException(status_code=404, detail="job not found")

    list = db.query(model.Queue).filter(model.Queue.job_id == job_id , model.Queue.status == 'pending').all()
    print(len(list))

    if len(list) != 0:
        raise HTTPException(status_code=425, detail="still shortlisting...")
    
    list = db.query(model.Queue).filter(model.Queue.job_id == job_id , model.Queue.status == 'success').all()
    return list
   
