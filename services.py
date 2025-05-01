import magic

from pikepdf import Pdf


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
