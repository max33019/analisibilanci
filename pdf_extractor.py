import pdfplumber
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    """
    Extracts all text from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text as a single string.
             Returns None if the file cannot be opened or processed.
    """
    text = ""
    logger.info(f"Attempting to extract text from PDF: {pdf_path}")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text:
            logger.info(f"Successfully extracted text from {pdf_path}.")
            return text.strip()
        else:
            logger.info(f"No text found in {pdf_path}.")
            return None
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {e}", exc_info=True)
        return None
