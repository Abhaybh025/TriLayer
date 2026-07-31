from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import numpy as np
from config.logging_config import get_logger

# logging
logger = get_logger(__name__)

logger.info("Initializing sentence transformer model")

load_dotenv()

model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text):
    """
    Generate embeddings for the given text using the pre-trained SentenceTransformer model.

    Args:
        text (str): The text for which to generate embeddings.

    Returns:
        np.ndarray: The generated embeddings.
    """
    logger.info("Generating embedding for text")
    try:
        embedding = model.encode(text)

        return embedding
    
    except Exception as e:
        logger.exception("Error generating embedding")
        raise
    
def semantic_similarity(resume_embeddings, jd_embeddings):
    """
    Calculate the semantic similarity between resume and job description embeddings.

    Args:
        resume_embeddings (np.ndarray): Embeddings of the resume text.
        jd_embeddings (np.ndarray): Embeddings of the job description text.

    Returns:
        float: The semantic similarity score between the resume and job description.
    """
    similarity = cosine_similarity(resume_embeddings.reshape(1, -1), jd_embeddings.reshape(1, -1))
    return float(similarity[0][0])

def semantic_match_score(resume_embeddings, jd_embeddings):
    """
    Calculate a semantic match score based on the similarity between resume and job description text.

    Args:
        resume_embeddings (np.ndarray): The embeddings of the resume text.
        jd_embeddings (np.ndarray): The embeddings of the job description text.
    Returns:
        float: The semantic match score between the resume and job description.
    """

    score = semantic_similarity(resume_embeddings, jd_embeddings)
    return round(score * 100, 2)