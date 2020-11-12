FROM python:3.6-buster

RUN mkdir /app
COPY ./requirements.txt /
#COPY . /app

RUN pip install --no-cache-dir -r /requirements.txt
RUN python -m spacy download en_core_web_sm
