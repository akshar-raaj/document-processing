Done
- Ability to upload a document
- Infer and Predict the document mime type
- Read contents of a PDF document.
- Explore PDF libraries
    - pikepdf: Py qpdf: Allows finding number of page, merging pdfs, splitting a pdf. Does not allow extracting PDF text.
    - pdfminer: Allows extracting PDF text
- Ability to merge multiple PDF documents into a single document
- Install Tesseract 
- Perform OCR and convert an image or a non searchable PDF to text
- Convert a searchable pdf to non-searchable pdf for performing OCR

TODO
- Allow ability to create a single PDF with 4 images.
- Perform text analysis on a file.
  - Find number of words.
  - Lexical Diversity
  - Top 10 words and their count

## Dependencies

### python-magic
Python interface to the libmagic, a file type identification library. Unix `file` command uses libmagic under the hood as well.
This uses file headers to identify the file mime type.

### pikepdf

A PDF manipulation library, based on qpdf.
