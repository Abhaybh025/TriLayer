from config.logging_config import get_logger

logger = get_logger(__name__)

import re

def ats_analysis(resume_text, matched_skills, missing_skills):
    """
    Perform ATS analysis on the resume text.

    Args:
        resume_text(str): Cleaned resume text.
        matched_skills(list): List of skills matched in the resume.
        missing_skills(list): List of skills missing in the resume.

    Returns:
        dict: A dictionary containing the analysis results.
    """

    logger.info("Performing ATS analysis")

    try: 
        score = 0
        feedback = []
        checks = {}

        # Check email
        email_pattern = r'\S+@\S+'

        if re.search(email_pattern, resume_text):
            score += 10
            checks["Email"] = True

        else:
            feedback.append("Email not found.")
            checks["Email"] = False

        # Check Phone
        phone_pattern = r'(\+?\d[\d\s-]{8,}\d)'

        if re.search(phone_pattern, resume_text):
            score += 10
            checks["Phone Number"] = True
        
        else:
            feedback.append("Phone not found.")
            checks["Phone Number"] = False

        # Check linkdln 
        if "linkedin" in resume_text.lower():
            score += 5
            checks["LinkedIn Profile"] = True
        else:
            feedback.append("Linkdln profile missing.")
            checks["LinkedIn Profile"] = False

        # Check github
        if "github" in resume_text.lower():
            score += 5
            checks["GitHub Profile"] = True

        else:
            feedback.append("GitHub profile missing.")
            checks["GitHub Profile"] = False

        # Section Detection 
        sections = {
            "skills":10,
            "experience":15,
            "education":10,
            "projects":15
        }

        for section, marks in sections.items():
            if section in resume_text.lower():
                score += marks
                checks[f"{section.title()} Section"] = True
            
            else:
                feedback.append(f"{section.title()} section missing.")
                checks[f"{section.title()} Section"] = False

        # Resume Length 
        words = len(resume_text.split())

        if words >= 300:
            score += 5
            checks["Resume Length"] = True
        
        else:
            feedback.append("Resume is too short.")
            checks["Resume Length"] = False

        # Action words 
        verbs = [
            "developed", "implemented", "designed", "optimized", "created", "built", "deployed"
        ]
        count = 0
        
        resume_lower = resume_text.lower()
        resume_words = set(resume_lower.split())

        for verb in verbs:

            if verb in resume_words:
                count += 1
        
        if count >= 3:
            score += 5
            checks["Action Verbs"] = True
        
        else:
            feedback.append("Use more action words.")
            checks["Action Verbs"] = False

        # Keyword Coverage
        if len(missing_skills) <= 2:
            score += 10
            checks["Keyword Coverage"] = True
        
        else:
            feedback.append("Many required keywords are missing.")
            checks["Keyword Coverage"] = False

        return {
            "ats_score": score,
            "feedback": feedback,
            "checks": checks
        }

    except Exception as e:
        logger.exception('Failed to perform ATS analysis')
        raise