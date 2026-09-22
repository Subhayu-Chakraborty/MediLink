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
pdf.cell(100, 8, 'Name: Aditya Kumar Singh', new_x="RIGHT", new_y="TOP")
pdf.cell(90, 8, f'Date: {datetime.now().strftime("%Y-%m-%d")}', new_x="LMARGIN", new_y="NEXT")

pdf.cell(100, 8, 'Age/Gender: 21 / Male', new_x="RIGHT", new_y="TOP")
pdf.cell(90, 8, 'Report ID: LAB-7891-CHK', new_x="LMARGIN", new_y="NEXT")

pdf.cell(100, 8, 'Referred By: Dr. Priya Sharma', new_x="RIGHT", new_y="TOP")
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

# Table Data
data = [
    ('Hemoglobin (Hb)', '15.2', 'g/dL', '13.8 - 17.2'),
    ('White Blood Cells (WBC)', '7.8', '10^3/uL', '4.5 - 11.0'),
    ('Platelet Count', '220', '10^3/uL', '150 - 450'),
    ('Fasting Blood Glucose', '108', 'mg/dL', '70 - 99 (HIGH)'),
    ('Total Cholesterol', '215', 'mg/dL', '< 200 (HIGH)'),
    ('LDL (Bad) Cholesterol', '135', 'mg/dL', '< 100 (HIGH)'),
    ('HDL (Good) Cholesterol', '42', 'mg/dL', '> 40'),
    ('Triglycerides', '180', 'mg/dL', '< 150 (HIGH)'),
    ('Serum Creatinine', '0.9', 'mg/dL', '0.7 - 1.3'),
    ('Systolic Blood Pressure', '128', 'mmHg', '< 120 (HIGH)'),
    ('Diastolic Blood Pressure', '82', 'mmHg', '< 80 (HIGH)'),
    ('Serum Iron', '90', 'mcg/dL', '65 - 175'),
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
    "Patient's hemoglobin, WBC count, platelet count, and kidney function markers are within normal limits. "
    "However, fasting blood glucose at 108 mg/dL indicates a pre-diabetic state and warrants dietary intervention. "
    "Lipid panel reveals borderline-high total cholesterol (215 mg/dL) and elevated LDL (135 mg/dL) and triglycerides (180 mg/dL), "
    "suggesting dyslipidemia. Blood pressure readings are mildly elevated. "
    "Recommend lifestyle modifications including a low-carb, low-fat diet, regular aerobic exercise (30 min/day), "
    "weight management, and a follow-up lipid panel and HbA1c in 3 months. "
    "If no improvement, pharmacotherapy may be considered."
)
pdf.multi_cell(0, 6, notes)

pdf.output('test_report_aditya.pdf')
print("PDF created successfully: test_report_aditya.pdf")
