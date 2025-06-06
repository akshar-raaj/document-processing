FROM python:3.11-bullseye

# Install system dependencies
# tesseract-ocr needed for pytesseract, to extract text from scanned images
# poppler-utils needed for pdftotext
# libgl1 needed for opencv
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

# Install spacy model that can perform NLP tasks like parts of speech tagging, named entity recognition and dependency parsing
RUN python -m spacy download en_core_web_sm

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]
CMD ["/app/start.sh"]
