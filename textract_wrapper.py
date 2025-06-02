from textract import detect_text

from db import set_object


def detect_text_and_set_db(file_path: str, key: str, field: str = 'content'):
    is_success, content = detect_text(file_path)
    if is_success is True:
        set_object(key, field, content)
        return True, content
    else:
        return False, content
