## What

This project performs the following broad functionalities:
- Text Extraction
- OCR (Optical Character Recognition)
- Text Analysis

It exposes an API endpoint `/ocr` that takes a PDF or an image as an input. It then performs OCR if needed on the input, extracts text out of the input, and outputs the extracted text.

An interactive API documentation is available at `/docs`. This API documentation is generated from an OpenAPI schema.

## How

### Dependencies

#### python-magic
Python interface to the libmagic, a file type identification library. Unix `file` command uses libmagic under the hood as well.
This uses file headers to identify the file mime type.

#### pikepdf
A PDF manipulation library, based on qpdf.
Allows performing PDF operations like rotating, cropping, merging etc.

#### pytesseract
Python interface to Tesseract OCR.
Tesseract OCR can take an image as in input, extract text from the input image, and can output to different formats.

#### pdf2image
It allows converting pdf pages to individual images.
Tesseract OCR can only be performed on image. Hence, we need ability to convert non searchable PDFs to images before performing OCR.

This has a dependency on poppler library.

#### pdfminer.six
It allows extracting text from searchable PDFs. In such cases on OCR is needed.

## TODO

Tesseract OCR is being used for performing OCR. It falls short while doing OCR on low quality images and handwritten text.
Hence, write an integration with Amazon Textract.