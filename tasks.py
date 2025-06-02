"""
rq integration

To use Redis Queue to handle the extraction tasks.

A guiding principle for tasks is that they should be self-contained.
Hence, the task itself should do any processing whether computational or I/O bound.
And once the task has completed, it is responsible for writing it to the database.
result_callbacks are messy, and we want to avoid them.
"""
from rq import Queue

# Only required to get the Redis connection which orchestrates the queue.
from db import get_connection


def enqueue_extraction(extraction_function, **kwargs):
    """
    Usage:
    enqueue_extraction(extraction_function=detect_text_and_set_db, file_path="/media/textract-ocr-files/abc.pdf", key="some-hash")
    """
    connection = get_connection()
    q = Queue(connection=connection)
    q.enqueue(extraction_function, **kwargs)
