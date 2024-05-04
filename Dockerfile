FROM python

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN pip install fastapi uvicorn

RUN pip install mysql-connector-python

RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.0/en_core_web_sm-2.2.0.tar.gz


COPY . .

ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
# sudo docker run --net=host --mount type=bind,source=/home/sarmad/Desktop/FYP_Resumes,target=/app/Resumes -u $(id -u $USER):$(id -g $USER) -p 8000:8000 fastapi
