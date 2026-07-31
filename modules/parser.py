import fitz
from config.logging_config import get_logger

# logging 
logger = get_logger(__name__)

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF resume file.
    
    Args:
        pdf_path(str) : Path to the PDF file.
        
    Returns:
        str: Extracted text
    """

    logger.info("Extracting text from PDF file: %s", pdf_path)
    
    text = ""

    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)

            text += page.get_text() + "\n"

        pdf_document.close()

        return text.strip()
    
    except Exception as e:
        logger.exception("Error extracting text from PDF")
        raise


def extract_text_from_txt(file_path = r"data\jd.txt"):
    """
    Extract text from a TXT file.
    
    Args:
        file_path (str): Path to the TXT file.
        
    Returns:
        str: Extracted text.
    """
    logger.info("Extracting text from TXT file: %s", file_path)

    try:
        # Open the TXT file and read its content
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    
    except Exception as e:
        logger.exception("Error extracting text from TXT file")
        raise

def is_resume_empty(text):
    """
    Check if the extracted resume text is empty or not.
        
    Args:
        text(str) : Extracted text from the resume.

    Returns:
        bool: True if the resume is empty, False otherwise.
    """

    return len(text.strip()) == 0

