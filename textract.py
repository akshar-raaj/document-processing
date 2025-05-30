"""
Integration with Amazon Textract for performing Text Detection and Optical Character Recognition.
"""
import boto3
import os
import logging


logger = logging.getLogger(__name__)


def detect_text(file_path: str):
    """
    Detects document text using AWS Textract.
    This is a synchronous and blocking operation.
    Textract Synchronous API only supports JPG and PNG formats. It doesn't support PDF format.

    Provide file path to a valid file.
    Textract supports JPEG, PNG.
    """
    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
    textract = boto3.client('textract', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='ap-south-1')
    f = open(file_path, "rb")
    content = f.read()
    try:
        response = textract.detect_document_text(Document={
            "Bytes": content
        })
        words = [block.get('Text') for block in response['Blocks'] if block.get('Text') is not None and block['BlockType'] == 'WORD']
        return True, " ".join(words)
    except Exception as exc:
        logger.error(f"Exception {exc} ocurred during Textract text detection.")
        return False, str(exc)
