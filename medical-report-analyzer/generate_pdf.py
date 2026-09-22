from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(0, 102, 204)
        self.cell(0, 10, 'MEDREPORT DIAGNOSTICS LABS', border=False, align='C')
        self.ln(10)
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, '123 Health Avenue, Wellness City, ST 12345 | Ph: 555-0199', border=False, align='C')
        self.ln(15)
        self.line(10, 30, 200, 30)

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
pdf.cell(100, 10, 'PATIENT INFORMATION', ln=False)
pdf.cell(90, 10, 'REPORT DETAILS', ln=True)

pdf.set_font('helvetica', '', 11)
pdf.cell(100, 8, 'Name: Lakshya', ln=False)
pdf.cell(90, 8, f'Date: {datetime.now().strftime("%Y-%m-%d")}', ln=True)

pdf.cell(100, 8, 'Age/Gender: 21 / Male', ln=False)
pdf.cell(90, 8, 'Report ID: LAB-9098-HTN', ln=True)

pdf.cell(100, 8, 'Referred By: Dr. Jane Smith', ln=False)
pdf.cell(90, 8, 'Sample Type: Blood / Serum', ln=True)

pdf.ln(5)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(5)

# Test Results Section
pdf.set_font('helvetica', 'B', 14)
pdf.cell(0, 10, 'COMPLETE BLOOD COUNT & METABOLIC PANEL', align='L', ln=True)
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
    ('White Blood Cells (WBC)', '8.4', '10^3/uL', '4.5 - 11.0'),
    ('Platelet Count', '210', '10^3/uL', '150 - 450'),
    ('Fasting Blood Glucose', '105', 'mg/dL', '70 - 99 (HIGH)'),
    ('Total Cholesterol', '220', 'mg/dL', '< 200 (HIGH)'),
    ('LDL (Bad) Cholesterol', '150', 'mg/dL', '< 100 (HIGH)'),
    ('HDL (Good) Cholesterol', '45', 'mg/dL', '> 40'),
    ('Triglycerides', '180', 'mg/dL', '< 150 (HIGH)'),
    ('Serum Creatinine', '0.9', 'mg/dL', '0.7 - 1.3'),
    ('Systolic Blood Pressure', '145', 'mmHg', '< 120 (HIGH)'),
    ('Diastolic Blood Pressure', '92', 'mmHg', '< 80 (HIGH)'),
]

pdf.set_font('helvetica', '', 10)
for row in data:
    # Highlight abnormal values
    if '(HIGH)' in row[3]:
        pdf.set_text_color(204, 0, 0)
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
pdf.cell(0, 10, 'CLINICAL OBSERVATIONS & NOTES:', ln=True)
pdf.set_font('helvetica', '', 10)
notes = (
    "Patient presents with Stage 1 Hypertension (145/92 mmHg) and borderline dyslipidemia. "
    "Fasting glucose is slightly elevated indicating pre-diabetic tendencies. "
    "Lifestyle modifications including dietary changes (low sodium, low saturated fat) and "
    "increased cardiovascular exercise are strongly recommended. Follow-up required in 3 months."
)
pdf.multi_cell(0, 6, notes)

pdf.output('test_report_lakshya.pdf')
print("PDF created successfully!")
