import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

def generate_pdf_report(name, total_score, breakdown, output_dir="C:\Coding\Automated-CV-Scoring\Outputs\Candidate_report"):
   
    os.makedirs(output_dir, exist_ok=True)

    safe_name = name.replace(" ", "_").replace("/", "_")
    output_file = os.path.join(output_dir, f"{safe_name}_report.pdf")

    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4
    text = c.beginText(1 * inch, height - 1 * inch)
    text.setFont("Helvetica-Bold", 16)
    text.textLine("Automated Resume Scoring Report")
    text.setFont("Helvetica", 12)
    text.textLine("")

    text.textLine(f"Candidate Name: {name}")
    text.textLine(f"Final Score: {total_score}/100")
    text.textLine("")
    text.textLine("Score Breakdown:")
    text.textLine("-----------------------------")

    for key, value in breakdown.items():
        if isinstance(value, float):
            value = round(value, 2)
        text.textLine(f"{key}: {value}")

    text.textLine("")
    text.textLine("Thank you for applying!")
    c.drawText(text)
    c.showPage()
    c.save()

    print(f"Report saved to {output_dir}")

    return os.path.abspath(output_file)
