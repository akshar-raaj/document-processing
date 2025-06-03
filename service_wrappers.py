import json
import logging

from services import extract_image_text, extract_pdf_text_all
from image_preprocessing import preprocess_image_opencv

from db import set_object
from text_analysis import classify, analyze_passport, analyze_pan


logger = logging.getLogger(__name__)


def extract_image_text_and_set_db(file_path: str, key: str, field: str = 'content', options=None):
    if options is None:
        options = {
            "gray": True,
            "denoise": True,
            "binarize": True
        }
    processed_image_path = preprocess_image_opencv(file_path, options)
    is_success, content = extract_image_text(processed_image_path)
    # TODO: Perform text analysis on another queue to not stall this queue
    if is_success is True:
        set_object(key, field, content)
        # Perform classification
        category = classify(content)
        logger.info(f"Category: {category}")
        if category is not None:
            set_object(key, "category", category)
            if category == 'passport':
                passport_data = analyze_passport(content)
                passport_data = json.dumps(passport_data)
                set_object(key, "passport_data", passport_data)
            elif category == 'pan':
                pan_data = analyze_pan(content)
                pan_data = json.dumps(pan_data)
                set_object(key, "pan_data", pan_data)
        # Extract structured data
        # Store structured data in DB
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
