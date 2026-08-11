# ocr_utils.py
# Utilities to extract numeric scores from an image using OpenCV + pytesseract.

import re
from typing import List, Optional
import cv2
import numpy as np
import pytesseract
from PIL import Image

# If tesseract is not in PATH on the host machine, set pytesseract.pytesseract.tesseract_cmd appropriately:
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # example for Linux

def preprocess_image_for_ocr(image_path: str) -> np.ndarray:
    """
    Read image and apply preprocessing to improve OCR accuracy:
    - convert to grayscale
    - apply bilateral filter (keeps edges)
    - adaptive threshold / Otsu
    - morphological opening to reduce noise
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot open image: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # scale up a bit for small images
    h, w = gray.shape
    scale_factor = 1.0
    if max(h, w) < 1000:
        scale_factor = 2.0
        gray = cv2.resize(gray, (int(w*scale_factor), int(h*scale_factor)), interpolation=cv2.INTER_CUBIC)

    # reduce noise but keep edges
    denoised = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

    # adaptive threshold
    th = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 31, 10)

    # morphological opening to remove small artifacts
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opened = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)

    return opened

def ocr_image_to_text(image_np: np.ndarray) -> str:
    """
    Run pytesseract on a preprocessed OpenCV image (numpy array).
    Restrict recognition to digits and common punctuation.
    """
    pil = Image.fromarray(image_np)
    config = r'--psm 6 -c tessedit_char_whitelist=0123456789-'
    text = pytesseract.image_to_string(pil, config=config)
    return text

def extract_integers_from_text(text: str) -> List[int]:
    """
    Extract signed integers from OCR text.
    """
    matches = re.findall(r'-?\d+', text)
    return [int(m) for m in matches]

def extract_scores_from_image(image_path: str, prefer_positive=True) -> List[int]:
    """
    Try multiple preprocessing strategies and return list of candidate integers found.
    The caller can then pick the best candidate (e.g., largest positive number).
    """
    candidates = set()
    # First pass – adaptive-threshold preprocess
    try:
        pre1 = preprocess_image_for_ocr(image_path)
        t1 = ocr_image_to_text(pre1)
        nums1 = extract_integers_from_text(t1)
        candidates.update(nums1)
    except Exception:
        pass

    # Second pass – Otsu threshold from original grayscale
    try:
        orig = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if orig is not None:
            # resize for small images
            h, w = orig.shape
            if max(h, w) < 1000:
                orig = cv2.resize(orig, (w*2, h*2), interpolation=cv2.INTER_CUBIC)
            _, th2 = cv2.threshold(orig, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            t2 = ocr_image_to_text(th2)
            nums2 = extract_integers_from_text(t2)
            candidates.update(nums2)
    except Exception:
        pass

    # Convert to sorted list
    cand_list = sorted(candidates)
    return cand_list

def choose_most_likely_score(candidates: List[int]) -> Optional[int]:
    """
    Heuristic to pick one score from candidate numbers:
    - Prefer positive numbers
    - Prefer values in a reasonable bridge score range (1..10000)
    - Prefer the largest reasonable number (often total points)
    """
    if not candidates:
        return None
    positives = [n for n in candidates if n > 0 and abs(n) < 100000]
    if positives:
        # If many small numbers, choose the largest — usually total points on the slip
        return max(positives)
    # fallback: any number
    return candidates[-1]
