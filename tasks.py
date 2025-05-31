"""
rq integration

To use Redis Queue to handle the extraction tasks.
"""
import hashlib
from rq import Queue

from db import get_connection, set_value


def report_success(job, connection, result, *args, **kwargs):
    is_success, extracted_text = result
    file_path = job.args[0]
    path_hash = hashlib.sha256(file_path.encode('utf-8')).hexdigest()
    # Write this result to the data store.
    set_value(path_hash, extracted_text)


def enqueue_extraction(extraction_function, file_path):
    connection = get_connection()
    q = Queue(connection=connection)
    q.enqueue(extraction_function, file_path, on_success=report_success)
