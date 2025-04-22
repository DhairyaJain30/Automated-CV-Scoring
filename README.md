# 🤖 Automated CV Scoring and Feedback AI Agent

This project is a smart, end-to-end system designed to **analyze resumes**, match them with a **job description**, **score candidates** based on multiple criteria, and **send personalized feedback via email**.

It helps recruiters **efficiently evaluate applicants**, and provides candidates with **detailed feedback**.

---

## 📌 Features

- ✅ **Resume Parsing** using a custom-trained Named Entity Recognition (NER) model  
- ✅ **JD–CV Matching** using a trained Doc2Vec model  
- ✅ **Rule-Based Scoring** across:
  - JD Match (40%)
  - Education (20%)
  - Experience (10%)
  - Relevant AI Skills (20%)
- ✅ **Automated Email Feedback** to candidates with detailed score breakdown  
 
## How to run 
1. Clone the repository
   git clone https://github.com/DhairyaJain30/Automated-CV-Scoring.git
   cd Automated-CV-Scoring
   
2.Download Requirements
  pip install -r requirements.txt

3.Run main function 
  python main.py

