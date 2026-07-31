import pandas as pd 
from config.logging_config import get_logger

# logging
logger = get_logger(__name__)

def load_skills(path = "data/skills.csv"):
    """
    Load skills from a CSV file.
    
    Args:
        path(str) : Path to the CSV file containing skills.

    Returns:
        list: A list of skills.
    """
    logger.info("Loading skills from CSV file: %s", path)

    try:
        skills_df = pd.read_csv(path)
        return set(
            skills_df['skill'].str.lower().str.strip()
        )
    except Exception as e:
        logger.exception("Error loading skills from CSV")
        raise

import re 

def extract_skills(text, skills_set):
    """
    Extract skills from the cleaned resume text based on a predefined set of skills.

    Args:
        text(str): Cleaned resume text.
        skills_set(set): A set of predefined skills to match against.
    Returns:
        list: A list of extracted skills found in the resume.
    """
    logger.info("Extracting skills from the text")

    try:
        extracted_skills = set()

        for skill in skills_set:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text):
                extracted_skills.add(skill)
        
        return list(extracted_skills)
    
    except Exception as e:
        logger.exception("Error extracting skills")
        raise


def compare_skills(resume_skills, jd_skills):
    """
    Compare the extracted skills from the resume with the required skills for a job.

    Args:
        resume_skills(list): A list of skills extracted from the resume.
        job_skills(list): A list of required skills for the job.

    Returns:
        dict: A dictionary containing matched skills and missing skills.
    """

    matched_skills = set(resume_skills) & set(jd_skills)
    missing_skills = set(jd_skills) - set(resume_skills)
    extra_skills = set(resume_skills) - set(jd_skills)

    return {
        "matched_skills": list(matched_skills),
        "missing_skills": list(missing_skills),
        "extra_skills": list(extra_skills)
    }

def skill_match_score(resume_skills, jd_skills):
    """
    Calculate a skill match score based on the number of matched skills and total required skills.

    Args:
        resume_skills(list): A list of skills extracted from the resume.
        job_skills(list): A list of required skills for the job.

    Returns:
        float: A score representing the percentage of required skills matched.
    """

    if len(jd_skills) == 0:
        return 0.0
    
    matched = len(set(resume_skills) & set(jd_skills))
    
    return round((matched / len(jd_skills)) * 100, 2)