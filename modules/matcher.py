from modules.skill_extractor import extract_skills, compare_skills, skill_match_score
from modules.embeddings import generate_embedding, semantic_match_score
from config.logging_config import get_logger

# logging 
logger = get_logger(__name__)

def analyze_resume(resume_text, jd_text, skills_set):
    """
    Analyze the resume and job description to extract skills and calculate match scores.

    Args:
        resume_text (str): The text of the resume.
        jd_text (str): The text of the job description.
        skills_set (set): A set of predefined skills to match against.
    Returns:
        dict: A dictionary containing extracted skills, comparison results, and match scores.
    """
    logger.info("Analyzing resume and job description")

    try:
        # Extract skills from resume and job description
        resume_skills = extract_skills(resume_text, skills_set)
        jd_skills = extract_skills(jd_text, skills_set)

        # Compare skills and calculate skill match score 
        skill_comparison = compare_skills(resume_skills, jd_skills)
        skill_score = skill_match_score(resume_skills, jd_skills)

        # Generate embeddings for semantic similarity
        resume_embeddings = generate_embedding(resume_text)
        jd_embeddings = generate_embedding(jd_text)

        # Calculate semantic match score
        semantic_score = semantic_match_score(resume_embeddings, jd_embeddings)

        # Calculating overall score as a weighted average of skill match score and semantic match score.
        overall_score = semantic_score * 0.7 + skill_score * 0.3

        # Strength detection 
        strengths = []
        if semantic_score > 80:
            strength = "Strong Sementic alignment with the job description."
            strengths.append(strength)

        if len(skill_comparison["matched_skills"]) >= 5:
            strength = "Good coverage of required technical skills."
            strengths.append(strength)

        if skill_score > 70:
            strength = "High skill match score."
            strengths.append(strength)

        # Weakness detection
        weaknesses = []
        if semantic_score < 50:
            weakness = "Weak semantic alignment with the job description."
            weaknesses.append(weakness)
        
        if len(skill_comparison["missing_skills"]) > 2:
            weakness = "Missing some required technical skills."
            weaknesses.append(weakness)
        
        if skill_score < 50:
            weakness = "Low skill match score."
            weaknesses.append(weakness)

        # Return the analysis results as a dictionary
        return {
            "resume_skills": resume_skills,
            "jd_skills": jd_skills,
            "overall_score": overall_score,
            "skill_score": skill_score,
            "semantic_score": semantic_score,
            "skill_comparison": skill_comparison,
            "matched_skills" : skill_comparison["matched_skills"],
            "missing_skills" : skill_comparison["missing_skills"],
            "extra_skills" : skill_comparison["extra_skills"],
            "strengths": strengths,
            "weaknesses": weaknesses
        }
    except Exception as e:
        logger.exception("Error analyzing resume")
        raise