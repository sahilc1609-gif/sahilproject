"""
Automated Project Report Generator
Converts the project documentation into:
  1. docs/project-report.docx (Microsoft Word format)
  2. docs/project-report.pdf (PDF format for Portal Submission)
"""

import os
import sys
from pathlib import Path

# Paths
DOCS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DOCS_DIR.parent
MD_PATH = DOCS_DIR / "PROJECT_REPORT.md"
DOCX_PATH = DOCS_DIR / "project-report.docx"
PDF_PATH = DOCS_DIR / "project-report.pdf"


def generate_docx():
    """Generates docs/project-report.docx using python-docx."""
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT

    doc = Document()

    # Document margins
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    # 1. Title / Cover Page Section
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run("ACADEMIC PROJECT REPORT\n\n")
    title_run.font.size = Pt(24)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(30, 58, 138)  # Deep Navy

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_p.add_run("SERVERLESS STUDENT RESULT MANAGEMENT SYSTEM\n\n")
    sub_run.font.size = Pt(18)
    sub_run.font.bold = True
    sub_run.font.color.rgb = RGBColor(15, 118, 110)  # Deep Teal

    desc_p = doc.add_paragraph()
    desc_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    desc_run = desc_p.add_run(
        "A Modular, Multi-Tiered Result Calculation & Cloud-Ready Management System\n"
        "Implemented in Python 3.14 with Dual CLI & AWS Lambda Architecture\n\n\n"
    )
    desc_run.font.size = Pt(12)
    desc_run.font.italic = True

    # Metadata box
    meta_p = doc.add_paragraph()
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_run = meta_p.add_run(
        "Submission Domain: Cloud Computing & Software Engineering\n"
        "Database Architecture: SQLite Local + DynamoDB Cloud Schema\n"
        "Status: Verified & 100% Test Validated\n"
        "Submission Date: September 2026\n"
    )
    meta_run.font.size = Pt(11)

    doc.add_page_break()

    # Read Markdown content and build Word document
    with open(MD_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_code_block = False
    code_lines = []

    for line in lines:
        stripped = line.rstrip()

        # Handle Code blocks
        if stripped.startswith("```"):
            if in_code_block:
                # End of code block
                in_code_block = False
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.2)
                r = p.add_run("\n".join(code_lines))
                r.font.name = "Consolas"
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(51, 65, 85)
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(stripped)
            continue

        # Headings
        if stripped.startswith("### "):
            h = doc.add_heading(level=2)
            hrun = h.add_run(stripped[4:])
            hrun.font.color.rgb = RGBColor(30, 58, 138)
        elif stripped.startswith("#### "):
            h = doc.add_heading(level=3)
            hrun = h.add_run(stripped[5:])
            hrun.font.color.rgb = RGBColor(15, 118, 110)
        elif stripped.startswith("## "):
            h = doc.add_heading(level=1)
            hrun = h.add_run(stripped[3:])
            hrun.font.color.rgb = RGBColor(30, 58, 138)
        elif stripped.startswith("# "):
            pass  # Already covered on cover page
        elif stripped.startswith("* ") or stripped.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            p.add_run(stripped[2:])
        elif stripped.startswith("---"):
            continue
        elif stripped:
            doc.add_paragraph(stripped)

    doc.save(DOCX_PATH)
    print(f"[+] DOCX report created successfully at: {DOCX_PATH}")


def generate_pdf():
    """Generates docs/project-report.pdf using reportlab."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted
    )

    pdf = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        alignment=1,  # Center
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=12
    )

    sub_title_style = ParagraphStyle(
        'CoverSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=1,
        textColor=colors.HexColor('#0F766E'),
        spaceAfter=20
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        alignment=1,
        textColor=colors.HexColor('#334155'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'H1Style',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0F766E'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        leftIndent=15,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        backColor=colors.HexColor('#F1F5F9'),
        textColor=colors.HexColor('#0F172A'),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # 1. Cover Page
    story.append(Spacer(1, 40))
    story.append(Paragraph("PROJECT REPORT SUBMISSION", title_style))
    story.append(Paragraph("SERVERLESS STUDENT RESULT MANAGEMENT SYSTEM", sub_title_style))
    story.append(Spacer(1, 20))

    meta_text = (
        "<b>Course / Domain:</b> Cloud Computing, Serverless Architecture & Software Engineering<br/>"
        "<b>Project Specification:</b> Multi-Tier Student Grading, Calculations, CLI & AWS Lambda Handlers<br/>"
        "<b>Database Engine:</b> Relational SQLite (Local) & DynamoDB Schema (Cloud Ready)<br/>"
        "<b>Testing Status:</b> 100% Automated Unit Test Validation (14/14 Tests Passed)<br/>"
        "<b>Candidate:</b> Student Project Submission<br/>"
        "<b>Date:</b> September 2026"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 40))

    # Summary table on cover page
    table_data = [
        ["Component", "Specification", "Status"],
        ["Language", "Python 3.14 (3.10+ compatible)", "Verified"],
        ["Architecture", "Decoupled 3-Tier (CLI / Services / DB)", "Implemented"],
        ["Cloud Engine", "AWS Lambda + API Gateway (serverless.yml)", "Configured"],
        ["Database", "SQLite (data/results.db)", "Normalized & Indexed"],
        ["Test Suite", "tests/test_app.py (14 Unit Tests)", "All Tests Pass"],
        ["Grading System", "A+, A, B+, B, C, P, F (Dual Pass/Fail Criteria)", "Engine Built"]
    ]
    t = Table(table_data, colWidths=[120, 260, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
    ]))
    story.append(t)
    story.append(PageBreak())

    # Parse PROJECT_REPORT.md content
    with open(MD_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_code_block = False
    code_buffer = []

    for line in lines:
        stripped = line.rstrip()

        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                code_text = "\n".join(code_buffer)
                # Escape XML entities for Preformatted / Paragraph
                clean_code = (code_text
                              .replace("&", "&amp;")
                              .replace("<", "&lt;")
                              .replace(">", "&gt;"))
                story.append(Preformatted(clean_code, code_style))
                story.append(Spacer(1, 4))
                code_buffer = []
            else:
                in_code_block = True
                code_buffer = []
            continue

        if in_code_block:
            code_buffer.append(stripped)
            continue

        if stripped.startswith("### "):
            story.append(Paragraph(stripped[4:], h1_style))
        elif stripped.startswith("#### "):
            story.append(Paragraph(stripped[5:], h2_style))
        elif stripped.startswith("## ") or stripped.startswith("# "):
            pass
        elif stripped.startswith("* ") or stripped.startswith("- "):
            clean_bullet = stripped[2:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"&bull; {clean_bullet}", bullet_style))
        elif stripped.startswith("---"):
            story.append(Spacer(1, 6))
        elif stripped:
            clean_p = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(clean_p, body_style))

    pdf.build(story)
    print(f"[+] PDF report created successfully at: {PDF_PATH}")


if __name__ == "__main__":
    generate_docx()
    generate_pdf()
