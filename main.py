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

 

    for file in os.listdir('/home/sarmad/Desktop/FYP_Resumes'):
        if fnmatch.fnmatch(file, user_id + '_*.pdf'):
            print(file)
            file_name = file

    reader = PdfReader('/home/sarmad/Desktop/FYP_Resumes/' + file_name)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    text = text.replace("  ", " ")
    print(text)

    nlp = spacy.load('en_core_web_sm')
    matcher = PhraseMatcher(nlp.vocab)
    nlp_text = nlp(text)
    # noun_chunks = nlp_text.noun_chunks
    # # removing stop words and implementing word tokenization
    # tokens = [token.text for token in nlp_text if not token.is_stop]
    
    # reading the csv file
    data = pd.read_csv("/home/sarmad/Go_Practice/PythonService/skills.csv") 

    terms1 = pd.read_csv("/home/sarmad/Go_Practice/PythonService/PhraseSkills.csv") 
    terms = list(terms1.columns.values)
    # extract values
    skills = list(data.columns.values)

    print(skills)
    print(terms)
    
    skillset = []
    
    # check for one-grams (example: python)
    for token in skills:
        if token in nlp_text.text:
            skillset.append(token)
    
    patterns = [nlp.make_doc(text) for text in terms]
    matcher.add("TerminologyList", None, *patterns)
    # check for bi-grams and tri-grams (example: machine learning)
    matches = matcher(nlp_text)
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        print(span.text)
        if span.text not in skillset:
            skillset.append(span.text)

    print(skillset)
    # print(noun_chunks)


    # data = ResumeParser('/home/sarmad/Desktop/FYP_Resumes/' + file_name).get_extracted_data()
    

    # # data = resumeparse.read_file('/home/sarmad/Desktop/FYP_Resumes/' + file)
    # print(data)
            

    


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
    
