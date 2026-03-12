import os
import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from mistralai import Mistral
from google import genai

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

INPUT_DOCS_DIR = Path(__file__).resolve().parent / "Input-docs"
OCR_OUTPUT_DIR = Path(__file__).resolve().parent / "ocr-output"
OUTPUT_FILE = Path(__file__).resolve().parent / "guidlines.json"


def get_mistral_client():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise EnvironmentError("MISTRAL_API_KEY is not set.")
    logger.info("Mistral client initialized.")
    return Mistral(api_key=api_key)


def get_gemini_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY is not set.")
    client = genai.Client(api_key=api_key)
    logger.info("Gemini client initialized.")
    return client


def read_pdf_files():
    pdf_files = sorted(INPUT_DOCS_DIR.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in %s", INPUT_DOCS_DIR)
    else:
        logger.info("Found %d PDF file(s) in %s", len(pdf_files), INPUT_DOCS_DIR)
    return pdf_files


def save_ocr_markdown(pdf_name, markdown_text):
    OCR_OUTPUT_DIR.mkdir(exist_ok=True)
    md_filename = Path(pdf_name).stem + ".md"
    md_path = OCR_OUTPUT_DIR / md_filename
    try:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        logger.info("OCR markdown saved to %s", md_path)
    except IOError as e:
        logger.error("Failed to save OCR markdown for %s: %s", pdf_name, e)


def write_json_output(data):
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Output written to %s", OUTPUT_FILE)
    except IOError as e:
        logger.error("Failed to write output file: %s", e)
        raise
