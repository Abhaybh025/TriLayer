import os
import streamlit as st
from frontend.components.sidebar import render_sidebar
from frontend.components.uploader import upload_resume, get_job_description_input
from modules.parser import extract_text_from_pdf, extract_text_from_txt
from modules.cleaner import clean_resume_text
from modules.skill_extractor import load_skills
from modules.matcher import analyze_resume
from modules.ats import ats_analysis
from modules.llm_analyzer import generate_llm_feedback
from frontend.components.metrics import render_metrics
from frontend.components.overview import render_overview
from frontend.components.skills import render_skills
from frontend.components.ats import render_ats
from frontend.components.llm_feedback import render_llm_feedback
from frontend.utils.style_loader import load_css
from frontend.components.header import render_header
from frontend.components.banner import render_banner


st.set_page_config(
    page_title="AI Resume Matcher",
    layout="wide"
)

# loading CSS
load_css()

# Loading the skills_db
skills_db = load_skills("data/skills.csv")

# render_sidebar()

render_header()

with st.container(border = True):

    st.subheader("Upload Documents")

    left, right = st.columns(
        [1,2],
        gap="large"
    )

    with left:
        # Calling upload_resume function 
        resume = upload_resume()

    with right:
        # Calling get JD input function -> it returns whether its text or file and the text or file respectively.
        input_type, jd  = get_job_description_input()


    st.divider()

    c1, c2, c3 = st.columns([1,2,1])

    with c2:
        # Adding analyze button
        analyze = st.button(
            "Analyze Resume",
            width="content"
        )

os.makedirs("temp", exist_ok=True)

# Integrating backend to analyze button
if analyze:
    # Handling Resume and extracting text from it.
    if resume is None:
        st.error(
            "Please upload a resume."
        )
        st.stop()

    resume_path = os.path.join(
        "temp",
        resume.name
    )

    try:

        # saving the uploaded resume to temp folder.
        with open(resume_path, "wb") as f:
            f.write(
                resume.getbuffer()
            )

        resume_text = extract_text_from_pdf(resume_path)

        cleaned_resume_text = clean_resume_text(resume_text)

        # Handling the Job Description Input and Extracting text from it.
        if input_type == "text":

            if not jd.strip():
                st.error("Please paste a Job description.")
                st.stop()
            
            jd_text = clean_resume_text(jd)

        else:
            if jd is None:
                st.error("Please upload a Job Description.")
                st.stop()

            jd_path = os.path.join("temp", jd.name)
            # Saving jd file in temp
            with open(jd_path,"wb") as f:
                f.write(jd.getbuffer())

            # if pdf extract text from it
            if jd.name.lower().endswith(".pdf"):
                jd_text = extract_text_from_pdf(jd_path)
            
            else:
                # if txt extract text from it
                jd_text = extract_text_from_txt(jd_path)

        # Calling analyze_resume function.
        analysis = analyze_resume(
            cleaned_resume_text,
            jd_text,
            skills_db
        )

        # Calling ATS analysis 
        ats_result = ats_analysis(
            clean_resume_text(resume_text, keep_urls=True),
            analysis["matched_skills"],
            analysis["missing_skills"]
        )

        # with st.expander("Matching Analysis"):

        #     st.json(analysis)

        # with st.expander("ATS Analysis"):

        #     st.json(ats_result)

        render_banner(
        analysis["overall_score"]
        )

        render_metrics(
            analysis,
            ats_result
        )

        llm_response = generate_llm_feedback(
            resume_text= clean_resume_text(cleaned_resume_text, keep_urls=True),
            jd_text=jd_text,
            analysis_result=analysis,
            ats_result=ats_result
        )

        overview_tab, skills_tab, ats_tab, ai_tab = st.tabs(
            [
                "Overview",
                "Skills",
                "ATS",
                "AI Feedback"
            ]
        )
        with overview_tab:
            render_overview(analysis)
        
        with skills_tab:
            render_skills(analysis)

        with ats_tab:
            render_ats(ats_result)

        with ai_tab:
            render_llm_feedback(llm_response)

    except Exception as e:
        st.error(f"An unexpected error occurred while analyzing the resume: {str(e)}")
        st.exception(e)

    finally:
        if os.path.exists(resume_path):
            os.remove(resume_path)
        
        if jd_path is not None and os.path.exists(jd_path):
            os.remove(jd_path)

        if not os.listdir("temp"):
            os.rmdir("temp")