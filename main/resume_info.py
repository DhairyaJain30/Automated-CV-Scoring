import fitz  
from docx import Document
import re
import spacy
from spacy.matcher import Matcher
import csv 
import json 
import os


# ------ Extracting Text From PDF and DOCS-------#
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        return ""

import re

#-------Text Cleaning------#

def clean_text(text):
    text = text.replace("-\n", "")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fix_common_broken_words(text):
    # define rules for frequent split words
    broken_fixes = {
        r"\bme nt\b": "ment",
        r"\bme rs\b": "mers",
        r"\bme ntal\b": "mental",
        r"\bme nts\b": "ments",
        r"\bms\b": "MS",  
        r"\bme dical\b": "medical",
        r"\bme ter\b": "meter",
        r"\bme d\b": "med"
    }
    for broken, fixed in broken_fixes.items():
        text = re.sub(broken, fixed, text, flags=re.IGNORECASE)
    return text

#------Extracting Contanct Number--------#

def extract_contact_number_from_resume(text):
    contact_number = None

    # Using regex pattern to find a potential contact number
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    if match:
        contact_number = match.group()

    return contact_number

# ------- Extracting Email--------#

def extract_email_from_resume(text):
    email = None

    # Using regex pattern to find a potential email address
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    if match:
        email = match.group()

    return email

#------- Extracting Skills From Resume------#

def extract_skills_from_resume(text, skills_list):
    skills = []

    for skill in skills_list:
        pattern = r"\b{}\b".format(re.escape(skill))
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            skills.append(skill)

    return skills

#----- Extracting Education From Resume------#
def extract_education_from_resume(text):
    education = []

    text = fix_common_broken_words(text)

    # Defining degree patterns with word boundaries
    degree_keywords = [
        r"B\.?\s?Tech(?:nology)?", r"M\.?\s?Tech(?:nology)?",
        r"B\.?\s?S(?:c|\.Sc)", r"M\.?\s?S(?:c|\.Sc)",
        r"\bBE\b", r"\bME\b", r"\bMS\b", r"\bMBA\b", r"Ph\.?D",
        r"Bachelor(?:'s)? of [\w\s]+", r"Master(?:'s)? of [\w\s]+"
    ]

    # Headers that might indicate education sections
    education_headers = [
        r"\bEDUCATION\b", r"\bACADEMIC(?:\s+BACKGROUND)?\b", r"\bQUALIFICATION(?:S)?\b"
    ]

    # Identify education sections if present
    education_sections = []
    for header in education_headers:
        matches = re.finditer(f"(?i){header}[:\s]*", text)
        for match in matches:
            start_idx = match.end()
            # Find the end of this section (next header or end of text)
            next_header = re.search(r"\n\s*[A-Z][A-Z\s]+[:\s]*\n", text[start_idx:])
            end_idx = start_idx + next_header.start() if next_header else len(text)
            education_sections.append(text[start_idx:end_idx])

    # If no education sections found, use the entire text
    text_to_analyze = education_sections if education_sections else [text]

    for segment in text_to_analyze:
        # First pass: Finding mentioned Degrees
        degree_pattern = r"(?i)(?<!\w)(" + "|".join(degree_keywords) + r")\b"
        degree_matches = re.finditer(degree_pattern, segment)

        for match in degree_matches:
            degree = match.group(1).strip()
            start_pos = match.end()

            
            rest_of_line = segment[start_pos:start_pos+150]  

            # Trying to find specialization after indicators like "in", "-", "with focus on", etc.
            specialization_match = re.search(r"(?:in|[-–—]|with\s+(?:focus|specialization)\s+(?:in|on)|specializing\s+in)\s+([A-Za-z][A-Za-z\s&,]+?)(?=\n|\.|,|$|with|from|\(|\d)", rest_of_line)

            if specialization_match:
                specialization = specialization_match.group(1).strip()
                # Filter out non-specialization text
                if len(specialization) > 3 and not re.search(r"\b(?:progress|year|college|university|institute|school)\b", specialization.lower()):
                    education.append(f"{degree} - {specialization}")
                    continue

            
            field_match = re.search(r"(?<!\w)([A-Z][a-z]+(?:\s+[A-Za-z][a-z]+){0,4})(?=\s+(?:Engineering|Technology|Science|Studies|Arts|Commerce|Management|Business|Administration))?", rest_of_line)

            if field_match:
                field = field_match.group(0).strip()
                # Make sure it's not just a school name or generic word
                if len(field) > 3 and not re.search(r"\b(?:university|college|institute|school|academy)\b", field.lower()):
                    education.append(f"{degree} - {field}")
                    continue

            # If all else fails, just record the degree
            education.append(degree)

    
    seen = set()
    unique_education = []
    for item in education:
        item_lower = item.lower()
        if item_lower not in seen:
            seen.add(item_lower)
            unique_education.append(item)
    return unique_education

#------- Extracting Work Experience------#

def extract_work_experience(text):
    """Extract work experience details including duration from resume text."""
    experiences = []

    text = fix_common_broken_words(text)

    # Look for experience sections
    exp_headers = [
        r"EXPERIENCE", r"EMPLOYMENT", r"WORK HISTORY", r"PROFESSIONAL EXPERIENCE",
        r"CAREER HISTORY", r"JOB HISTORY", r"WORK EXPERIENCE"
    ]

    # Finding experience section
    experience_sections = []
    for header in exp_headers:
        matches = re.finditer(fr"(?i)\b{header}\b[:\s]*", text)
        for match in matches:
            start_idx = match.end()
            next_header = re.search(r"\n\s*[A-Z][A-Z\s]+[:\s]*\n", text[start_idx:])
            end_idx = start_idx + next_header.start() if next_header else len(text)
            experience_sections.append(text[start_idx:end_idx])

    text_to_analyze = experience_sections if experience_sections else [text]

    for segment in text_to_analyze:
        # Looking for company names 
        company_pattern = r"(?:^|\n)[\s]*([A-Z][A-Za-z\s&,.]+(?:Inc|LLC|Ltd|Corp|Corporation|Company)?)\s*(?:\n|,|;|-|–)"
        companies = re.finditer(company_pattern, segment)

        for company_match in companies:
            company = company_match.group(1).strip()
            position_start = company_match.end()

            # Looking for dates nearby 
            context = segment[position_start:position_start+200]

            # Trying to find job title
            title_match = re.search(r"(?i)([\w\s]+(?:Engineer|Developer|Scientist|Analyst|Manager|Director|Assistant|Specialist|Consultant|Coordinator|Associate|Lead|Head|Chief|Officer|VP|President|Intern))", context)
            title = title_match.group(1).strip() if title_match else "Unknown Position"

            # Looking for date ranges
            date_pattern = r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]*(?:19|20)\d{2}|(?:19|20)\d{2})[^\n\d]+((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]*(?:19|20)\d{2}|(?:19|20)\d{2}|Present|Current|Now)"
            date_match = re.search(date_pattern, context, re.IGNORECASE)


            experiences.append({
                "company": company,
                "title": title,
            })

    # If no experiences are found, return None
    if not experiences:
        return None

    return experiences

#------- Extracting Names ------#

def extract_name(resume_text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(resume_text)

    # Collecting all potential proper noun chunks (up to 3 words)
    name_candidates = []
    for i in range(len(doc) - 1):
        if doc[i].pos_ == "PROPN" and doc[i+1].pos_ == "PROPN":
            chunk = [doc[i].text]
            j = i + 1
            while j < len(doc) and doc[j].pos_ == "PROPN" and len(chunk) < 3:
                chunk.append(doc[j].text)
                j += 1
            full_name = " ".join(chunk)
            name_candidates.append(full_name)

    # Pick the first candidate with max 3 words
    for name in name_candidates:
        if 2 <= len(name.split()) <= 3:
            return name
    if name_candidates:
        return name_candidates[0]

    return None

# ------ Saving Data in JSON Format ----- #

def save_to_json(parsed_data):
    """Save parsed resume data to a JSON file in a specific directory with candidate's name."""
    
    # Define the directory
    directory = r"C:\Coding\Automated-CV-Scoring\Outputs\Candidate_data"
    os.makedirs(directory, exist_ok=True)
    
    # Extract candidate's name 
    candidate_name = parsed_data.get('name', 'Unknown_Candidate').replace(" ", "_").replace("/", "_")
    
    file_path = os.path.join(directory, f"{candidate_name}_extracted_resume_data.json")
    
    # Save the data to the specified JSON file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(parsed_data, file, ensure_ascii=False, indent=4)
    
    print(f"Data saved to {file_path}")

#------- Full Resume Parsing ------ #
           
def full_resume_parser(text, skills_list):
    extracted_data = {}

    name = extract_name(text)
    extracted_data["name"] = name if name else None

    contact_number = extract_contact_number_from_resume(text)
    extracted_data["phone"] = contact_number if contact_number else None

    email = extract_email_from_resume(text)
    extracted_data["email"] = email if email else None

    work_exp = extract_work_experience(text)
    extracted_data["experience"] = work_exp if work_exp else None

    extracted_skills = extract_skills_from_resume(text, skills_list)
    extracted_data["skills"] = extracted_skills

    extracted_data['Education'] = extract_education_from_resume(text)

    extracted_data["raw_text"] = text

    return extracted_data

# ------- Main Function------#

def parse_resume(file_path):
    skills_list = [
        'Python', 'Data Analysis', 'Machine Learning', 'LLM', 'Transformer',
        'AI Agents', 'Flask', 'GenAI', 'TensorFlow', 'Communication',
        'Project Management', 'Deep Learning', 'SQL', 'Tableau',
        'Leadership', 'Team Work', 'Management','Power BI'
    ]

    raw_text = extract_text(file_path)
    text = clean_text(raw_text)
    parsed_data = full_resume_parser(text, skills_list)
    save_to_json(parsed_data)
    return parsed_data


