"""
PDF Generator Module
Converts markdown analysis text to formatted PDF for email attachment
"""

import re
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def parse_analysis_sections(analysis_text):
    """
    Parse the markdown analysis into structured sections
    Returns dict with: critical_issues, important_issues, minor_issues, overall_assessment
    """
    sections = {
        'critical_issues': '',
        'important_issues': '',
        'minor_issues': '',
        'overall_assessment': '',
        'critical_count': 0,
        'important_count': 0,
        'minor_count': 0
    }

    # Split by major section headers (match ## heading format)
    critical_match = re.search(r'##\s*CRITICAL ISSUES.*?\n(.*?)(?=##\s*IMPORTANT ISSUES|##\s*MINOR ISSUES|##\s*OVERALL|$)',
                              analysis_text, re.DOTALL | re.IGNORECASE)
    important_match = re.search(r'##\s*IMPORTANT ISSUES.*?\n(.*?)(?=##\s*MINOR ISSUES|##\s*OVERALL|$)',
                               analysis_text, re.DOTALL | re.IGNORECASE)
    minor_match = re.search(r'##\s*MINOR ISSUES.*?\n(.*?)(?=##\s*OVERALL|$)',
                           analysis_text, re.DOTALL | re.IGNORECASE)
    overall_match = re.search(r'##\s*OVERALL.*?\n(.*?)$',
                             analysis_text, re.DOTALL | re.IGNORECASE)

    if critical_match:
        sections['critical_issues'] = critical_match.group(1).strip()
        # Count issues (look for ### 1., ### 2., etc. or plain numbered items)
        sections['critical_count'] = len(re.findall(r'^###\s*\d+\.', sections['critical_issues'], re.MULTILINE))
        if sections['critical_count'] == 0:
            sections['critical_count'] = len(re.findall(r'^\s*[-•*]\s+', sections['critical_issues'], re.MULTILINE))
        if sections['critical_count'] == 0:
            sections['critical_count'] = len(re.findall(r'^\s*\d+\.', sections['critical_issues'], re.MULTILINE))

    if important_match:
        sections['important_issues'] = important_match.group(1).strip()
        sections['important_count'] = len(re.findall(r'^###\s*\d+\.', sections['important_issues'], re.MULTILINE))
        if sections['important_count'] == 0:
            sections['important_count'] = len(re.findall(r'^\s*[-•*]\s+', sections['important_issues'], re.MULTILINE))
        if sections['important_count'] == 0:
            sections['important_count'] = len(re.findall(r'^\s*\d+\.', sections['important_issues'], re.MULTILINE))

    if minor_match:
        sections['minor_issues'] = minor_match.group(1).strip()
        sections['minor_count'] = len(re.findall(r'^###\s*\d+\.', sections['minor_issues'], re.MULTILINE))
        if sections['minor_count'] == 0:
            sections['minor_count'] = len(re.findall(r'^\s*[-•*]\s+', sections['minor_issues'], re.MULTILINE))
        if sections['minor_count'] == 0:
            sections['minor_count'] = len(re.findall(r'^\s*\d+\.', sections['minor_issues'], re.MULTILINE))

    if overall_match:
        sections['overall_assessment'] = overall_match.group(1).strip()

    return sections


def clean_markdown_for_pdf(text):
    """
    Clean markdown formatting for PDF display
    """
    # Remove markdown bold
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)

    # Remove markdown italic
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)

    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


def generate_pdf_from_analysis(analysis_text):
    """
    Generate a PDF from the analysis markdown text
    Returns: BytesIO object containing the PDF
    """
    buffer = BytesIO()

    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Parse sections
    sections = parse_analysis_sections(analysis_text)

    # Container for PDF elements
    story = []

    # Define styles
    styles = getSampleStyleSheet()

    # Custom title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#667eea'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Custom heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#667eea'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    # Body text style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        spaceAfter=6,
        leading=14
    )

    # Add title
    story.append(Paragraph("Home Inspection Analysis Report", title_style))
    story.append(Spacer(1, 0.2*inch))

    # Add generation date
    date_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    story.append(Paragraph(date_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    # Add summary table
    story.append(Paragraph("Summary", heading_style))
    summary_data = [
        ['Issue Category', 'Count'],
        ['Critical Issues', str(sections['critical_count'])],
        ['Important Issues', str(sections['important_count'])],
        ['Minor Issues', str(sections['minor_count'])]
    ]

    summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f9f9f9')),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dddddd')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))

    # Add detailed sections
    if sections['critical_issues']:
        story.append(Paragraph("1. CRITICAL ISSUES (Must Address Immediately)", heading_style))
        cleaned_text = clean_markdown_for_pdf(sections['critical_issues'])
        for paragraph in cleaned_text.split('\n\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), body_style))
        story.append(Spacer(1, 0.2*inch))

    if sections['important_issues']:
        story.append(Paragraph("2. IMPORTANT ISSUES (Should Address Soon)", heading_style))
        cleaned_text = clean_markdown_for_pdf(sections['important_issues'])
        for paragraph in cleaned_text.split('\n\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), body_style))
        story.append(Spacer(1, 0.2*inch))

    if sections['minor_issues']:
        story.append(Paragraph("3. MINOR ISSUES (Low Priority)", heading_style))
        cleaned_text = clean_markdown_for_pdf(sections['minor_issues'])
        for paragraph in cleaned_text.split('\n\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), body_style))
        story.append(Spacer(1, 0.2*inch))

    if sections['overall_assessment']:
        story.append(Paragraph("4. OVERALL ASSESSMENT", heading_style))
        cleaned_text = clean_markdown_for_pdf(sections['overall_assessment'])
        for paragraph in cleaned_text.split('\n\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), body_style))

    # Build PDF
    doc.build(story)

    # Get PDF bytes
    buffer.seek(0)
    return buffer
