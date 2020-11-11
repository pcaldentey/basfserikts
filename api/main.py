import os
import pika
import psycopg2
import shutil
import time
import zipfile


from fastapi import FastAPI
from fastapi import UploadFile, File
from pathlib import Path


QUEUE_NAME = os.getenv('QUEUE_NAME')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')

app = FastAPI()


def unzip_artifact(local_directory, file_path):
    fileName, ext = os.path.splitext(file_path)
    if ext == ".zip":
        zipfile.ZipFile(file_path).extractall(local_directory)


@app.get("/")
def root():
    return {"msg": "You have available all swagger docs in http://0.0.0.0/docs"}


@app.post("/upload-file/")
async def create_upload_file(uploaded_file: UploadFile = File(...)):
    # Copy file
    file_location = f"files/{uploaded_file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(uploaded_file.file, file_object)

    # Extract file
    name, _ = os.path.splitext(uploaded_file.filename)
    local_folder = "files/{}".format(time.time())
    try:
        os.mkdir(local_folder)
        unzip_artifact(local_folder, file_location)
    except OSError as e:
        print(e)
        return {"error": "Creation of the directory %s failed" % local_folder}

    except zipfile.error as e:
        print(e)

    # Publish patents in rabbit
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.queue_declare(queue=QUEUE_NAME + "2")
    for f in Path(local_folder).glob('*.xml'):
        with open('{}/{}'.format(local_folder, f.name), 'r') as fp:
            lines = fp.readlines()
            channel.basic_publish('', QUEUE_NAME, ''.join(lines))

    return {"info": f"file '{uploaded_file.filename}' saved at '{file_location}' and processed"}


@app.get("/clear")
def get_clear():
    # Delete queue
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit'))
    channel = connection.channel()
    channel.queue_delete(queue=QUEUE_NAME)
    channel.queue_delete(queue=QUEUE_NAME + "2")
    # Cleaning database
    try:

        conn = psycopg2.connect(
            host="postgresql",
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS)

        cur = conn.cursor()

        # execute a statement
        cur.execute('TRUNCATE TABLE named_entity')
        cur.execute('TRUNCATE TABLE patent')

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return {"status": "OK"}
