from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(0, 102, 204)
        self.cell(0, 10, 'MEDREPORT DIAGNOSTICS LABS', border=False, align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, '123 Health Avenue, Wellness City, ST 12345 | Ph: 555-0199', border=False, align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        self.line(10, 30, 200, 30)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

pdf = PDF()
pdf.add_page()

# Patient Information
pdf.set_font('helvetica', 'B', 12)
pdf.set_text_color(0)
pdf.cell(100, 10, 'PATIENT INFORMATION', new_x="RIGHT", new_y="TOP")
pdf.cell(90, 10, 'REPORT DETAILS', new_x="LMARGIN", new_y="NEXT")

pdf.set_font('helvetica', '', 11)
pdf.cell(100, 8, 'Name: Subhayu', new_x="RIGHT", new_y="TOP")
pdf.cell(90, 8, f'Date: {datetime.now().strftime("%Y-%m-%d")}', new_x="LMARGIN", new_y="NEXT")

pdf.cell(100, 8, 'Age/Gender: 22 / Male', new_x="RIGHT", new_y="TOP")
pdf.cell(90, 8, 'Report ID: LAB-5432-CHK', new_x="LMARGIN", new_y="NEXT")

pdf.cell(100, 8, 'Referred By: Dr. Alan Grant', new_x="RIGHT", new_y="TOP")
pdf.cell(90, 8, 'Sample Type: Blood / Serum', new_x="LMARGIN", new_y="NEXT")

pdf.ln(5)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(5)

# Test Results Section
pdf.set_font('helvetica', 'B', 14)
pdf.cell(0, 10, 'COMPLETE BLOOD COUNT & METABOLIC PANEL', align='L', new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

# Table Header
pdf.set_fill_color(220, 230, 241)
pdf.set_font('helvetica', 'B', 10)
pdf.cell(60, 10, 'TEST DESCRIPTION', border=1, fill=True)
pdf.cell(40, 10, 'RESULT', border=1, fill=True, align='C')
pdf.cell(30, 10, 'UNITS', border=1, fill=True, align='C')
pdf.cell(60, 10, 'REFERENCE RANGE', border=1, fill=True, align='C')
pdf.ln()

# Table Data (Mostly normal, slight iron deficiency/anemia markers)
data = [
    ('Hemoglobin (Hb)', '13.1', 'g/dL', '13.8 - 17.2 (LOW)'),
    ('White Blood Cells (WBC)', '6.2', '10^3/uL', '4.5 - 11.0'),
    ('Platelet Count', '250', '10^3/uL', '150 - 450'),
    ('Fasting Blood Glucose', '85', 'mg/dL', '70 - 99'),
    ('Total Cholesterol', '165', 'mg/dL', '< 200'),
    ('LDL (Bad) Cholesterol', '90', 'mg/dL', '< 100'),
    ('HDL (Good) Cholesterol', '55', 'mg/dL', '> 40'),
    ('Triglycerides', '110', 'mg/dL', '< 150'),
    ('Serum Creatinine', '1.0', 'mg/dL', '0.7 - 1.3'),
    ('Systolic Blood Pressure', '118', 'mmHg', '< 120'),
    ('Diastolic Blood Pressure', '76', 'mmHg', '< 80'),
    ('Serum Iron', '55', 'mcg/dL', '65 - 175 (LOW)'),
]

pdf.set_font('helvetica', '', 10)
for row in data:
    if '(LOW)' in row[3] or '(HIGH)' in row[3]:
        pdf.set_text_color(204, 102, 0)
        pdf.set_font('helvetica', 'B', 10)
    else:
        pdf.set_text_color(0)
        pdf.set_font('helvetica', '', 10)
        
    pdf.cell(60, 10, row[0], border=1)
    pdf.cell(40, 10, row[1], border=1, align='C')
    pdf.cell(30, 10, row[2], border=1, align='C')
    pdf.cell(60, 10, row[3], border=1, align='C')
    pdf.ln()

pdf.ln(10)

# Doctor Notes
pdf.set_text_color(0)
pdf.set_font('helvetica', 'B', 12)
pdf.cell(0, 10, 'CLINICAL OBSERVATIONS & NOTES:', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('helvetica', '', 10)
notes = (
    "Patient's general metabolic panel and lipid profile are well within normal ranges. "
    "Cardiovascular and kidney function markers appear excellent. "
    "However, Hemoglobin and Serum Iron levels are slightly below the reference range, "
    "suggesting mild iron deficiency anemia. Recommend increasing dietary intake of iron-rich foods "
    "(spinach, lentils, red meat) and a follow-up CBC in 6 months."
)
pdf.multi_cell(0, 6, notes)

pdf.output('test_report_subhayu.pdf')
print("PDF created successfully!")
