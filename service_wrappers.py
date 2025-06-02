from services import extract_image_text, extract_pdf_text_all
from image_preprocessing import preprocess_image_opencv

from db import set_object


def extract_image_text_and_set_db(file_path: str, key: str, field: str = 'content', options=None):
    if options is None:
        options = {
            "gray": True,
            "denoise": True,
            "binarize": True
        }
    processed_image_path = preprocess_image_opencv(file_path, options)
    is_success, content = extract_image_text(processed_image_path)
    if is_success is True:
        set_object(key, field, content)
        return True, content
    else:
        return False, content


def extract_pdf_text_and_set_db(file_path: str, key: str, field: str = 'content'):
    is_success, content = extract_pdf_text_all(file_path)
    if is_success is True:
        set_object(key, field, content)
        return True, content
    else:
        return False, content
