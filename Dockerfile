FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6

COPY ./requirements-api.txt /
#COPY ./api /app

RUN pip install --no-cache-dir -r /requirements-api.txt
