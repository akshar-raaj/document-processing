import magic

from pikepdf import Pdf
from pdfminer.high_level import extract_text


def identify_file_type(file_object_or_stream):
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


def merge_pdfs(attachments):
    """
    Merges multiple PDFs using pikepdf.
    pikepdf is a Python binding that interfaces with qpdf. qpdf allows reading, manipulating and creating pdfs.

    A list of `UploadFile` is passed as attachments.
    """
    merged_pdf = Pdf.new()
    filenames = []
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
    merged_pdf.save(f"/media/merged-pdfs/{merged_filename}")
    merged_pdf.close()
    return merged_filename


async def save_pdf(attachment, path):
    # Open in binary mode
    # We aren't doing raw I/O, as we haven't disabled buffering.
    # By default Python operates in buffered mode.
    chunk_size = 1024 * 1024   # 1 MB
    file = open(path, "wb")
    while True:
        # Reading will be performed in buffered mode.
        chunk = await attachment.read(chunk_size)
        if not chunk:
            break
        file.write(chunk)
    file.close()
    print("Saved PDF")


def extract_pdf_text(attachment):
    """
    Extracts text from a PDF containing embedded text using pdfminer.six library.

    It wouldn't be able to extract text from PDFs which don't have embedded text i.e in scanned PDFs or PDFs having images of text.
    """
    text = extract_text(attachment)
    return text
