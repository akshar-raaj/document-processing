"""
This module is supposed to only import Python built-ins or third-party libraries.

It can import application module only if that module too adherese to the above policy.
"""

import os
import glob
import logging
from typing import List, BinaryIO

# File mime-type detection
import magic
from magic.compat import FileMagic

# PDF manipulation
from pikepdf import Pdf

# PDF text extraction
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError

# Image text extraction
# OCR can only happen on images, OCR doesn't work with PDF
import pytesseract
from pytesseract.pytesseract import TesseractError

# Convert non-searchable PDFs to images before performing OCR
from pdf2image import convert_from_path

from fastapi import UploadFile

from text_analysis import is_meaningful_content


logger = logging.getLogger(__name__)


def identify_file_type(file_object_or_stream: BinaryIO) -> FileMagic:
    """
    Identifies the file's MIME type using magic.
    It's a Python interface to libmagic library. It behaves similar to
    Unix `file` command.
    It uses magic numbers present in the files to infer the file type.

    The beauty of this library is that it doesn't rely on file extension. Instead uses the file's content, magic numbers to be precise, to indentify the file's mime type.

    :param: A file like object.
    A file like object has methods like `read`, `readline` etc.
    The client is responsible for giving a file like object or stream and for closing the file.

    There are methods like `detect_from_filename` as well. However, since
    we anyways have a file object, we will use that.
    """
    result = magic.detect_from_fobj(file_object_or_stream)
    return result


def merge_pdfs(attachments: List[UploadFile]) -> str:
    """
    Merges multiple PDFs using pikepdf.
    pikepdf is a Python binding that interfaces with qpdf. qpdf allows reading, manipulating and creating pdfs.

    A list of `UploadFile` is passed as attachments.
    We considered passing File instances. UploadFile.file is possible however FastAPI UploadFile.file lacks a filename. Hence we decided on passing the `UploadFile` itself.
    """
    merged_pdf = Pdf.new()
    logger.info("Created a new PDF")
    filenames = []
    for attachment in attachments:
        stream = attachment.file
        original_filename = attachment.filename
        filename = attachment.filename
        if '.pdf' in filename:
            filename = filename.replace('.pdf', '')
        filenames.append(filename)
        pdf = Pdf.open(stream)
        merged_pdf.pages.extend(pdf.pages)
        logger.info(f"Merged {original_filename}")
    merged_filename = "-".join(filenames)
    merged_filename = f"{merged_filename}.pdf"
    merged_pdf.save(f"/media/merged-pdfs/{merged_filename}")
    merged_pdf.close()
    logger.info("Merged PDF saved")
    return merged_filename


def save_file(file: BinaryIO, path: str):
    # Open in binary mode
    # We aren't doing raw I/O, as we haven't disabled buffering.
    # By default Python operates in buffered mode.
    logger.info(f"Saving file to {path}")
    chunk_size = 1024 * 1024   # 1 MB
    out_file = open(path, "wb")
    while True:
        # Reading will be performed in buffered mode.
        chunk = file.read(chunk_size)
        if not chunk:
            break
        out_file.write(chunk)
    out_file.close()
    logger.info(f"Saved file to {path}")


def extract_pdf_text_searchable(file: BinaryIO):
    """
    :param: A file like object, opened in binary mode.
    Extracts text from a PDF containing embedded text using pdfminer.six library.
    It also works for scanned PDFs having images of text, as long as the PDF is searchable, i.e contains hidden embedded text.

    It wouldn't be able to extract text from PDFs which don't have embedded text i.e in scanned PDFs or PDFs having images of text.
    """
    try:
        text = extract_text(file)
        return True, text
    except PDFSyntaxError:
        return False, "An invalid or corrupted PDF"


def extract_pdf_text_non_searchable(file_path: str):
    """
    :param: A PDF file path.
    Extracts text from non searchable PDFs i.e scanned PDFs that don't have embedded text.
    Converts a PDF to an image and then extracts text from it. Delegates to extract_image_text which
    performs OCR using Pytesseract.
    """
    output_folder = "/media/pdf-to-image"   # Directory name -> /media/pdf-to-image
    basename = os.path.basename(file_path)       # File name -> sample.pdf
    if '.pdf' in basename:
        basename = basename.replace('.pdf', '')
    convert_from_path(file_path, output_folder=output_folder, fmt="png", output_file=basename)
    # The converted images have been saved now.
    converted_images_paths = sorted(glob.glob(f"{output_folder}/{basename}*.png"))
    is_successes = []
    contents = []
    for converted_image_path in converted_images_paths:
        is_success, content = extract_image_text(converted_image_path)
        is_successes.append(is_success)
        if is_success is True:
            # Only concatenate the contents from pages that we were able to extract.
            contents.append(content)
        else:
            logger.info(f"Failed to extract text from {converted_image_path}")
    return any(is_successes), "\n".join(contents)


def extract_pdf_text_all(file_path: str):
    """
    Attempts extraction for both searchable and non-searchable PDFs.

    1. For searchable_pdfs, delegate to extract_pdf_text which uses pdfminer.six
    2. For non-searchable PDFs, convert to an image and then extract text
    """
    f = open(file_path, "rb")
    is_success, content = extract_pdf_text_searchable(f)
    f.close()
    if is_success is False:
        # It's not even a PDF probably
        return False, content
    if is_meaningful_content(content):
        return True, content
    is_success, content = extract_pdf_text_non_searchable(file_path)
    return is_success, content


def get_file_size(file):
    file.seek(0, 2)   # Move to the end of file
    size = file.tell()
    file.seek(0)   # Reset back to beginning
    return size


def extract_image_text(file_path: str):
    """
    Expects an image file path to be passed.
    A TesseractError would happen, and will be handled, if the file is non-image.
    """
    try:
        text = pytesseract.image_to_string(file_path)
        return True, text
    except TesseractError:
        return False, "An invalid or corrupted image"
