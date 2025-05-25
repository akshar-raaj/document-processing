import logging
from typing import List

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services import identify_file_type, merge_pdfs, save_file, extract_pdf_text, get_file_size, extract_image_text, extract_pdf_text_all
from services import text_analysis


app = FastAPI()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# Allow CORS for your frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    logger.info("Root invoked")
    return "Document Processing"


@app.post("/content-type")
def identify_content_type(attachment: UploadFile):
    # Identify the file mime type.
    filename = f"/media/content-type-identification/{attachment.filename}"
    save_file(attachment.file, filename)
    # We read through the file in the last step, i.e save_file().
    # We must seek(0), and go to the beginning before trying to identify the file type.
    attachment.file.seek(0)
    file_type = identify_file_type(attachment.file)
    return {"content-type": file_type.mime_type}


@app.post("/pdfs-merge")
def pdfs_merge(attachments: List[UploadFile]):
    """
    Allows uploading multiple PDFs as multipart/form-data.
    It stitches the PDFs together and stores the new PDF.
    """
    # First validate that all the attachments are PDFs.
    if len(attachments) > 10:
        raise HTTPException(status_code=400, detail=f"A maximum of 10 attachments are allowed.")
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


@app.post("/extract-pdf-text")
def extract_text(attachment: UploadFile):
    """
    Extracts text from an attachment uploaded through multipart/form-data.
    """
    type_details = identify_file_type(attachment.file)
    if type_details.mime_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="A non-pdf file found.")
    attachment_name = attachment.filename
    output_filename = f"/media/extraction-pdfs/{attachment_name}"
    save_file(attachment.file, output_filename)
    attachment.file.seek(0)
    is_success, content = extract_pdf_text(attachment.file)
    if is_success is False:
        raise HTTPException(status_code=400, detail=content)
    analysis_result = text_analysis(content)
    return {"content": content, "analysis_result": analysis_result}


@app.post("/extract-image-text")
def extract_img_text(attachment: UploadFile):
    """
    Perform OCR on the uploaded attachment.
    Currently works with images having text.
    Later add support for PDFs and Docx as well.
    """
    type_details = identify_file_type(attachment.file)
    if not type_details.mime_type.startswith('image'):
        raise HTTPException(status_code=400, detail="A non image file found.")
    file_size = get_file_size(attachment.file)
    # 100 MB
    if file_size > (10 * 1024 * 1024):
        raise HTTPException(status_code=400, detail="Only supports upto 10MB files.")
    output_filename = f"/media/extraction-images/{attachment.filename}"
    attachment.file.seek(0)
    save_file(attachment.file, output_filename)
    is_success, content = extract_image_text(output_filename)
    if is_success is False:
        raise HTTPException(status_code=400, detail=content)
    return {"content": content}


@app.post("/ocr")
def ocr(attachment: UploadFile):
    """
    TODO: Support multiple attachments
    It could pass a PDF or an image.
    A PDF could be searchable or non-searchable.

    Image Case:
    We can run the image file through tesseract and extract the text.

    PDF Case:
    Searchable: We can use pdfminer.six as being used.
    Non-Searchable: Covert the PDF to an image and then extract the text

    In all of the above cases, the text should be extracted and returned from here.
    """
    type_details = identify_file_type(attachment.file)
    if not type_details.mime_type.startswith('image') and not type_details.mime_type.startswith('application/pdf'):
        raise HTTPException(status_code=400, detail="Provide either an image or a PDF")
    # 1. Save the attachment, for later auditing
    output_filename = f"/media/ocr-files/{attachment.filename}"
    save_file(attachment.file, output_filename)
    attachment.file.seek(0)
    # Check the content-type, if image, then extract text using Tesseract.
    if type_details.mime_type.startswith('image'):
        is_success, content = extract_image_text(output_filename)
    elif type_details.mime_type.startswith('application/pdf'):
        # Attempt extracting text using pdfminer.six or else through the image conversion -> OCR pipeline.
        is_success, content = extract_pdf_text_all(file_path=output_filename)
    if is_success is True:
        return content
    else:
        raise HTTPException(400, detail=content)
