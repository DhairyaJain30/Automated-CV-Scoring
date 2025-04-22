ai_skills_master = [
    "Machine Learning", "Deep Learning", "NLP", "CNN", "Transformer",
    "LLM", "GEN AI", "AI Agents", "Scikit learn", "Tensorflow",
    "Pytorch", "Spacy", "BERT", "Flask", "Python"
]

def get_education_score(education_text):
    if isinstance(education_text, list):
        education_text = " ".join(education_text)
    education_text = education_text.lower()

    if any(degree in education_text for degree in ["mba", "m.tech", "ms"]):
        return 20
    elif "b.tech" in education_text:
        return 18
    elif "bca" in education_text or "mca" in education_text:
        return 15
    elif "bsc" in education_text or "msc" in education_text:
        return 10
    return 0


def get_experience_score(experience):
    # If no experience is found (None), return 0
    if experience is None or len(experience) == 0:
        return 0
    else:
        return 10


def get_skills_score(extracted_skills):
    skills_found = 0

    
    if isinstance(extracted_skills, str):
        extracted_skills = extracted_skills.lower().split(',')
    elif isinstance(extracted_skills, list):
        extracted_skills = [skill.lower() for skill in extracted_skills]

    for skill in extracted_skills:
        skill = skill.strip()
        if any(ai.lower() in skill for ai in ai_skills_master):
            skills_found += 1

    return min(skills_found, 10) * 2  


def calculate_score(jd_score,parsed_data):
    
    jd_score_ = jd_score
    education = parsed_data["Education"]
    experience = parsed_data["experience"]
    skills = parsed_data["skills"]

    edu_score = get_education_score(education)
    exp_score = get_experience_score(experience)
    skill_score = get_skills_score(skills)

    final_score = (
        edu_score + exp_score +skill_score
        + (jd_score_ *(0.5))
        )
    
        

    return round(final_score, 2), {
        "JD_CV Match Score": round(jd_score * 0.5),
        "Education Score": edu_score,
        "Experience Score": exp_score,
        "AI Skills Score": skill_score,
    }
