import os
import logging
import hashlib
import json
from typing import List

from fastapi import FastAPI
from fastapi import UploadFile, Form
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import ConverseModel
from services import identify_file_type, merge_pdfs, save_file
from service_wrappers import extract_image_text_and_set_db, extract_pdf_text_and_set_db
from textract_wrapper import detect_text_and_set_db
from language_processing import converse
from tasks import enqueue_extraction
from db import set_object, get_object


app = FastAPI()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# Allow CORS for your frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001", "http://ocr.petprojects.in", "http://nlp.petprojects.in"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    logger.info("Root invoked")
    return "Document Processing"


@app.post("/pdfs-merge")
def pdfs_merge(attachments: List[UploadFile]):
    """
    Allows uploading multiple PDFs as multipart/form-data.
    It stitches the PDFs together and stores the new PDF.
    """
    # First validate that all the attachments are PDFs.
    if len(attachments) > 10:
        raise HTTPException(status_code=400, detail="A maximum of 10 attachments are allowed.")
    logger.info("Performing mime type validation on attachments.")
    for attachment in attachments:
        # Save the attachment for further analysis
        filename = f"/media/original-pdfs/{attachment.filename}"
        save_file(attachment.file, filename)
        attachment.file.seek(0)  # Reset the pointer to the file beginning
        file_type = identify_file_type(attachment.file)
        mime_type = file_type.mime_type
        if file_type.mime_type != 'application/pdf':
            logger.info(f"Validation on {filename} failed.")
            raise HTTPException(status_code=400, detail=f"A {mime_type} file posted.")
    # Validation passed
    merged_filename = merge_pdfs(attachments)
    return {"status": "processed", "filename": merged_filename}


@app.post("/ocr")
def ocr(attachment: UploadFile, gray: bool = Form(True), denoise: bool = Form(True), binarize: bool = Form(True)):
    """
    TODO: Support multiple attachments
    It could pass a PDF or an image.
    A PDF could be searchable or non-searchable.

    Image Case:
    We can run the image file through tesseract and extract the text.

    PDF Case:
    Searchable: We can use pdfminer.six as being used.
    Non-Searchable: Covert the PDF to an image and then extract the text

    In all of the above cases, the processing would happen asynchronously.
    The task would be queued and a link would be returned to the user.
    """
    options = {
        "gray": gray,
        "denoise": denoise,
        "binarize": binarize
    }
    type_details = identify_file_type(attachment.file)
    if not type_details.mime_type.startswith('image') and not type_details.mime_type.startswith('application/pdf'):
        raise HTTPException(status_code=400, detail="Provide either an image or a PDF")
    # 1. Save the attachment, for later auditing
    output_filename = f"/media/ocr-files/{attachment.filename}"
    save_file(attachment.file, output_filename)
    attachment.file.seek(0)
    path_hash = hashlib.sha256(output_filename.encode('utf-8')).hexdigest()
    # Check the content-type, if image, then extract text using Tesseract.
    if type_details.mime_type.startswith('image'):
        # Attempt extraction through Tesseract
        set_object(key=path_hash, field="type", value="image")
        enqueue_extraction(extraction_function=extract_image_text_and_set_db, file_path=output_filename, key=path_hash, options=options)
    elif type_details.mime_type.startswith('application/pdf'):
        # Attempt extracting text using pdfminer.six or else through the image conversion -> OCR pipeline.
        set_object(key=path_hash, field="type", value="pdf")
        enqueue_extraction(extraction_function=extract_pdf_text_and_set_db, file_path=output_filename, key=path_hash)
    # Add it to a queue.
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
    link = f"{BASE_URL}/ocr-result/{path_hash}"
    return {"link": link}


@app.get("/ocr-result/{key}")
def ocr_result(key: str):
    content = get_object(key, "content")
    if content is None:
        return {"content": content}
    response_data = {}
    category = get_object(key, "category")
    if category is not None:
        # Only if category is not None, then include it in the response
        response_data["category"] = category
        if category == 'passport':
            passport_data = get_object(key, "passport_data")
            passport_data = json.loads(passport_data)
            response_data["passport_data"] = passport_data
        elif category == 'pan':
            pan_data = get_object(key, "pan_data")
            pan_data = json.loads(pan_data)
            response_data["pan_data"] = pan_data
    # Remove empty lines
    lines = content.splitlines()
    non_blank_lines = [line for line in lines if line.strip() != '']
    content = '\n'.join(non_blank_lines)
    response_data["content"] = content
    return response_data


@app.post("/textract-ocr")
def textract_ocr(attachment: UploadFile):
    type_details = identify_file_type(attachment.file)
    if not type_details.mime_type.startswith('image'):
        raise HTTPException(status_code=400, detail="Provide an image")
    output_filename = f"/media/textract-ocr-files/{attachment.filename}"
    save_file(attachment.file, output_filename)
    attachment.file.seek(0)
    path_hash = hashlib.sha256(output_filename.encode('utf-8')).hexdigest()
    set_object(key=path_hash, field="type", value="pdf")
    # Add it to a queue.
    enqueue_extraction(extraction_function=detect_text_and_set_db, file_path=output_filename, key=path_hash)
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
    link = f"{BASE_URL}/ocr-result/{path_hash}"
    return {"link": link}


@app.post("/converse")
def conversation(body: ConverseModel):
    """
    Performs things like:
    - Tokenization
    - Parts of Speech tagging
    - Named Entity Recognition
    """
    answer = converse(body.text, body.question)
    logger.info(f"Answer: {answer}")
    if answer is None:
        answer = "Failed to parse"
    return {"answer": answer}
