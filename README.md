![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
<!--Taken from https://github.com/Ileriayo/markdown-badges-->

![GitHub last commit](https://img.shields.io/github/last-commit/akshar-raaj/document-processing) ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/akshar-raaj/document-processing/lint.yml)

## What

This repository powers the following:
- [http://ocr.petprojects.in](http://ocr.petprojects.in)
- [http://nlp.petprojects.in](http://nlp.petprojects.in)

This project performs the following broad functionalities:
- Text Detection
- Text Extraction
- OCR (Optical Character Recognition)
- Text Analysis

It exposes an API endpoint `/ocr` that takes a PDF or an image as an input. It then performs OCR if needed on the input, extracts text out of the input, and outputs the extracted text.

`/ocr` performs OCR using Tesseract. Another API endpoint `/textract-ocr` performs OCR using **AWS Textract**. AWS Textract provides better accuracy on low quality images, skewed images and images of handwritten text.

An interactive API documentation is available at `/docs`, see http://ocr-api.petprojects.in/docs. This API documentation is generated from an OpenAPI schema.

## How

### Dependencies

The following Python dependencies makes OCR possible.

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

#### boto3
Provides Python interfaces to AWS Services. We are using AWS Textract.

### AWS Textract
AWS Textract is a critical component for performing accurate text recognition and detection on low quality or skewed images.

Example AWS CLI command:

    aws textract detect-document-text --document '{"S3Object":{"Bucket":"annals","Name":"decathlon-whey.jpeg"}}' --profile administrator --region ap-south-1 --debug

### nltk
It is being used to perform Natural Language Processing. We have the ability to analyse the extracted text and infer:
- Word Frequency
- Repetitions and Lexical Diversity
- Parts of Speech Tagging
- Named Entity Recognition

For advanced purposes, we might explore using spaCy.

### rq
rq(Redis Queue) is being used to enqueue the OCR extraction tasks on a Redis List. Workers running in the background dequeue from this list and invoke the service functions to perform actual OCR.

### opencv-contrib-python
Provides Computer Vision and Image processing capability. We preprocess the image before performing recognition and detection.
We apply grayscaling, smoothing and denoising, and thresholding and binarisation.
