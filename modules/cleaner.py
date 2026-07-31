import re 
from config.logging_config import get_logger

# Logging 
logger = get_logger(__name__)

def clean_resume_text(
        text,
        keep_urls = False,
    ):
    """
    Clean resume/JD text

    Args:
        text(str): Raw text to be cleaned.

    Returns:
        str: Cleaned text
    """

    logger.info("Cleaning resume text")
    
    try:
        ## lowercase 
        text = text.lower()
        #print('After lowercasing:', text)

        if (not keep_urls):
            ## remove urls and domains
            text = re.sub(r'http\S+|www\S+|\S+\.(com|org|net|in)\S*', ' ', text)

            ## remove emails
            text = re.sub(r'\S+@\S+', ' ', text)

            ## phone numbers
            text = re.sub(r'\+?\d[\d\s\-]{8,}\d', ' ', text)

        ## remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        #print('After removing extra spaces:', text)

        return text.strip()
    
    except Exception as e:
        logger.exception("Error cleaning text: %s", e)
        raise

def count_words(text):
    """
    Count the number of words in the cleaned text.

    Args:
        text(str): Cleaned text.

    Returns:
        int: Number of words in the text.
    """

    return len(text.split())


from collections import Counter

def get_top_n_words(text, n=10):
    """
    Get the top n most common words in the cleaned text.

    Args:
        text(str): Cleaned text.
        n(int): Number of top words to return.

    Returns:
        list: List of top n most common words.
    """

    words = text.split()

    return Counter(words).most_common(n)