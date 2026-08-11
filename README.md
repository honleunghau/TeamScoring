# Bridge Score Compare (Prototype)

This prototype compares two images of bridge score sheets, extracts the scores using OCR, computes the point difference, and converts the difference to IMPs (standard WBF table).

Prerequisites
- Python 3.10+ recommended
- Tesseract OCR installed on the host machine:
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
  - macOS (Homebrew): `brew install tesseract`
  - Windows: install from https://github.com/tesseract-ocr/tesseract/releases and add to PATH

Install Python dependencies:
```bash
python -m pip install -r requirements.txt
