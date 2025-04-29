from fastapi import FastAPI
from fastapi import UploadFile

from utils import identify_file_type


app = FastAPI()


@app.get("/")
def root():
    return "Document Processing"


@app.post("/upload")
async def upload(attachment: UploadFile):
    path = f"/media/{attachment.filename}"
    f = open(path, "wb")
    chunk = await attachment.read(1024 * 1024)
    while chunk:
        f.write(chunk)
        chunk = await attachment.read(1024 * 1024)
    f.close()
    # Identify the file mime type.
    file_type = identify_file_type(path)
    print(file_type)
    return {"status": "processed"}
