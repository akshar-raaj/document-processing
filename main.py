from typing import List

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi.exceptions import HTTPException

from pikepdf import Pdf

from utils import identify_file_type


app = FastAPI()


@app.get("/")
def root():
    return "Document Processing"


@app.post("/content-type")
async def identify_content_type(attachment: UploadFile):
    # Identify the file mime type.
    file_type = identify_file_type(attachment.file)
    return {"content-type": file_type.mime_type}


@app.post("/pdfs-merge")
def pdfs_merge(attachments: List[UploadFile]):
    """
    Allows uploading multiple PDFs as multipart/form-data.
    It stitches the PDFs together and stores the new PDF.
    """
    merged_pdf = Pdf.new()
    filenames = []
    # First validate that all the attachments are PDFs.
    for attachment in attachments:
        file_type = identify_file_type(attachment.file)
        mime_type = file_type.mime_type
        if file_type.mime_type != 'application/pdf':
            raise HTTPException(status_code=400, detail=f"A {mime_type} file posted.")
    # Validation passed
    for attachment in attachments:
        stream = attachment.file
        filename = attachment.filename
        if '.pdf' in filename:
            filename = filename.replace('.pdf', '')
        filenames.append(filename)
        pdf = Pdf.open(stream)
        merged_pdf.pages.extend(pdf.pages)
    merged_filename = "-".join(filenames)
    merged_filename = f"{merged_filename}.pdf"
    merged_pdf.save(f"/media/{merged_filename}")
    merged_pdf.close()
    return {"status": "processed", "filename": merged_filename}
