FROM python:3.11-bullseye

# Install system dependencies
# tesseract-ocr needed for pytesseract, to extract text from scanned images
# poppler-utils needed for pdftotext
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]
