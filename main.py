from fastapi import FastAPI
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import Request, FastAPI, Depends
import redis 
import fnmatch
import os
from pyresparser import ResumeParser
from resume_parser import resumeparse
import pandas as pd
from PyPDF2 import PdfReader
import spacy
from spacy.matcher import PhraseMatcher

from schema import DataSchema
from database import SessionLocal, engine
import model
import worker
import asyncio

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

# endpoint for extracting skills from resume when user uploads it.

@app.post("/extract")
async def read_item(request: Request, db:Session=Depends(get_database_session)):
    user_id = await request.json()
    file_name: str
    # print(user_id)

    # getting the matched file name
    for file in os.listdir('/home/sarmad/Desktop/FYP_Resumes'):
        if fnmatch.fnmatch(file, user_id + '_*.pdf'):
            print(file)
            file_name = file

    # reading matched file
    reader = PdfReader('/home/sarmad/Desktop/FYP_Resumes/' + file_name)
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
    
    # reading the csv files
    data = pd.read_csv("/home/sarmad/Go_Practice/PythonService/skills.csv") 
    data2 = pd.read_csv("/home/sarmad/Go_Practice/PythonService/PhraseSkills.csv") 

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

    


@app.post("/{job_id}")
async def read_item(job_id, request: Request, db:Session=Depends(get_database_session)):
    print(job_id)
    # users = []
    resultList = await request.json()
    print(resultList)
    
    # Adding record to database
    for x in resultList["Users"]:
    #     print(x)
        record = model.Queue()
        record.job_id = job_id
        record.user_id = x
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
        redis_client.lpush(queue_name, x)

    await worker.shortlist_worker()
