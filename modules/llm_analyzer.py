import os 
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate 
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from config.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()

class ResumeAnalysis(BaseModel):
    overall_evaluation: str = Field(
        description="Overall resume evaluation"
    )
    strengths: list[str] = Field(
        description="Strengths of the resume."
    )

    weaknesses: list[str] = Field(
        description="Weaknesses of the resume."
    )

    missing_skills: list[str] = Field(
        description="Missing technical skills."
    )

    ats_improvements: list[str] = Field(
        description="ATS improvement suggestions."
    )

    resume_improvements: list[str] = Field(
        description="General resume improvement suggestions."
    )

    final_recommendation: str = Field(
        description="Final hiring recommendation."
    )

llm  = ChatGroq(
    model = "openai/gpt-oss-20b",
    temperature = 0,   
)

structured_llm = llm.with_structured_output(ResumeAnalysis)

def create_prompt():

    logger.info("Creating a prompt template.")

    try:

        prompt = ChatPromptTemplate.from_template(
        """
        You are an experienced technical recruiter and ATS expert.

        Analyze the following resume against the job description.

        Resume: {resume}
        Job description: {jd}

        Current Analysis 
        Overall score: {overall_score}

        Semantic Score: {semantic_score}

        Skill Score: {skill_score}

        ATS Score: {ats_score}

        Matched Skills: {matched_skills}

        Missing Skills: {missing_skills}

        Extra Skills: {extra_skills}

        Strengths Detected: {strengths}

        Weaknesses Detected: {weaknesses}

        Provide:
        1. Overall Evaluation
        2. Strengths
        3. Weaknesses
        4. Missing Technical Skills
        5. ATS Improvements
        6. Resume Improvement Suggestions
        7. Final Recommendation

        Keep the response professional and concise.
        """
        )

        logger.info("Prompt template created successfully.")
        return prompt
    
    except Exception as e:
        logger.error('Failed to create prompt template')
        raise

def generate_llm_feedback(
        resume_text,
        jd_text,
        analysis_result,
        ats_result
):

    logger.info("Generating LLM feedback")

    try:
        prompt = create_prompt()
        logger.info("LLM chain created successfully.")

        chain = prompt | structured_llm

        response = chain.invoke({
            "resume" : resume_text,
            "jd" : jd_text,
            "overall_score" : analysis_result["overall_score"],
            "semantic_score" : analysis_result["semantic_score"],
            "skill_score" : analysis_result["skill_score"],
            "matched_skills": analysis_result["matched_skills"],
            "missing_skills" : analysis_result["missing_skills"],
            "extra_skills" : analysis_result["extra_skills"],
            "strengths" : analysis_result["strengths"],
            "weaknesses" : analysis_result["weaknesses"],
            "ats_score" : ats_result["ats_score"]
        })
        logger.info("LLM response received successfully.")
        return response

    except Exception as e:
        logger.error("Failed to generate LLM feedback")
        raise

