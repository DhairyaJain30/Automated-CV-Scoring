import os
from resume_info import parse_resume
from jd_cv_match import compute_similarity
from score import calculate_score
from generate_report import generate_pdf_report
from email_sender import send_email_with_attachment

def run_pipeline(resume_path, jd_text):
    print("[1] Parsing resume...")
    parsed_data = parse_resume(resume_path)
    candidate_name = parsed_data.get("name", "Candidate")
    candidate_email= parsed_data.get("email","Candidate")

    print("[2] JD–CV matching...")
    jd_score = compute_similarity(jd_text, parsed_data["raw_text"])

    print("[3] Calculating scores...")
    total_score, score_breakdown = calculate_score(jd_score,parsed_data)

    print("[5] Creating PDF report...")
    report_path = generate_pdf_report(candidate_name, total_score, score_breakdown)


    print("[6] Sending email...")
    send_email_with_attachment(candidate_email, candidate_name, report_path)

    print("✅ Pipeline completed!")


if __name__ == "__main__":
    # Input for resume path 
    resume_path = input("Enter the path to your resume: ")

    # Input for job description file path (txt format)
    jd_path = input("Enter the path to the job description file: ")

    # Read the job description text
    with open(jd_path, 'r', encoding='utf-8') as f:
        jd_text = f.read()

