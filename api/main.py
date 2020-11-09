import shutil

from fastapi import FastAPI
from fastapi import UploadFile, File


app = FastAPI()


@app.get("/")
def root():
    return {"msg": "You have available all swagger docs in http://0.0.0.0/docs"}


@app.post("/upload-file/")
async def create_upload_file(uploaded_file: UploadFile = File(...)):
    file_location = f"files/{uploaded_file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(uploaded_file.file, file_object)
    return {"info": f"file '{uploaded_file.filename}' saved at '{file_location}'"}


@app.get("/clear")
def get_clear():
    errors = []
    connected = True
    if errors:
        return {"errors": errors}
    elif connected:
        return {"connected": True, "organisations": None}
    else:
        return {"connected": False}
