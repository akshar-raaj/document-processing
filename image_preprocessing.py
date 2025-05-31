"""
Responsible for doing image preprocessing. Image preprocessing is need to make the image clearer, crispier and easier to read.

OCR performs better if the image is:
    - grayscale
    - denoised
    - binarised

grayscale conversion: Convert from RGB space to grayscale space. Thus converting a color image into a black-and-white image. Each pixel represents intensity rather than color. Reduces complexity from 3 color channels to 1.
denoised: Applies filters and removes dots, specks and blurs. Currently MedianBlur algorithm is being used with Pillow.
binarised: Convert grayscale image to binary. Removed background clutter. Each pixel becomes either black(0) or white(255). Dark becomes darker and light becomes lighter.

TODO:
- DPI Normalization: to make the image crispier and easy to read
- Contour detection

Currently we are using Pillow, which is basic. We can move to opencv which has better denoising and binarization support. Also it supports contour detection and DPI normalization.
"""

import os
import logging
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)


def preprocess_image(file_path: str):
    try:
        base, ext = os.path.splitext(file_path)
        ext = ext.lstrip(".")
        im = Image.open(file_path)
        image_grayscale = im.convert("L")
        image_denoised = image_grayscale.filter(ImageFilter.MedianFilter(size=3))
        image_binary = image_denoised.point(lambda x: 0 if x < 128 else 255, mode='1')
        output_path = f"{base}-processed.{ext}"
        image_binary.save(output_path)
        return output_path
    except Exception as exc:
        logger.error(f"Exception {exc} ocurred during image preprocessing.")
        return file_path
