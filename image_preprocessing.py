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
- Border Removal
- Erosion and Dilation
- Edge detection
- Rotation and Alignment

Currently we are using Pillow, which is basic. We can move to opencv which has better denoising and binarization support. Also it supports contour detection and DPI normalization.
"""

import os
import logging
from PIL import Image, ImageFilter
import cv2 as cv

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


def preprocess_image_opencv(file_path: str, options: dict = None, source: str = "image"):
    """
    source could be one of 'image' or 'pdf'. We will apply fastNlMeansDenoising to PDF pages converted to images,
    while apply bilateralFilter to camera images.

    Currently performs:
    - Color space conversion from RGB to Grayscale, to make the image easier to read
    - Denoising, Smoothing and Blurring to remove specks/grains, using fastNlMeansDenoising or bilateralFilter
    - Binarisation, to have black text on a white background

    TODO:
    - Cropping the area of interest
    - Rotation and Alignment: Using Canny, HoughLines.
    """
    default_options = {
        "gray": True,
        "denoise": True,
        "binarize": True,
    }
    if options is None:
        options = {}
    default_options.update(options)
    logger.info(f"file_path: {file_path}, options: {default_options}")
    base, ext = os.path.splitext(file_path)
    ext = ext.lstrip(".")
    img = cv.imread(file_path)
    if default_options['denoise'] is True and default_options['gray'] is False:
        # Force grayscale, as denoising is done in grayscale
        logger.info("Forcing grayscale, as denoising is done in grayscale")
        default_options['gray'] = True
    if default_options['gray'] is True:
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    if default_options['denoise'] is True:
        if source == "pdf":
            logger.info("Applying fastNlMeansDenoising")
            img = cv.fastNlMeansDenoising(img, h=30)
        else:
            logger.info("Applying bilateralFilter")
            # It smoothes the image without losing edges
            img = cv.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
    if default_options['binarize'] is True:
        img = cv.adaptiveThreshold(
            img,
            maxValue=255,
            adaptiveMethod=cv.ADAPTIVE_THRESH_GAUSSIAN_C,  # or MEAN_C
            thresholdType=cv.THRESH_BINARY,
            blockSize=11,  # size of the neighborhood (must be odd)
            C=2            # constant subtracted from the mean
        )
    # Check if dilation and erosion needed
    # Find the margins and crop
    output_path = f"{base}-cv-processed.{ext}"
    cv.imwrite(output_path, img)
    return output_path
