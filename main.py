import logging
from typing import List

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi.exceptions import HTTPException

from services import identify_file_type, merge_pdfs


app = FastAPI()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


@app.get("/")
def root():
    logger.info("Root invoked")
    return "Document Processing"


@app.post("/content-type")
def identify_content_type(attachment: UploadFile):
    # Identify the file mime type.
    file_type = identify_file_type(attachment.file)
    # We are not persisting this file on the server
    return {"content-type": file_type.mime_type}


@app.post("/pdfs-merge")
def pdfs_merge(attachments: List[UploadFile]):
    """
    Allows uploading multiple PDFs as multipart/form-data.
    It stitches the PDFs together and stores the new PDF.
    """
    filenames = []
    # First validate that all the attachments are PDFs.
    if len(attachments) > 10:
        raise HTTPException(status_code=400, detail=f"A maximum of 10 attachments are allowed.")
    logger.info("Performing mime type validation on attachments.")
    for attachment in attachments:
        file_type = identify_file_type(attachment.file)
        mime_type = file_type.mime_type
        if file_type.mime_type != 'application/pdf':
            raise HTTPException(status_code=400, detail=f"A {mime_type} file posted.")
    # Validation passed
    merged_filename = merge_pdfs(attachments)
    return {"status": "processed", "filename": merged_filename}
