"""
Email Service Module
Handles sending emails with PDF attachments via Gmail SMTP
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email_validator import validate_email, EmailNotValidError

from pdf_generator import generate_pdf_from_analysis, parse_analysis_sections
from email_templates import render_html_email, render_text_email


def send_email_with_pdf(recipient_email, analysis_text, sender_name=None):
    """
    Send analysis email with PDF attachment via Gmail SMTP

    Args:
        recipient_email: Email address of recipient
        analysis_text: Full markdown analysis text
        sender_name: Optional sender name for email display

    Returns:
        Tuple of (success: bool, message: str)
    """

    try:
        # Validate email format
        try:
            valid = validate_email(recipient_email)
            recipient_email = valid.email  # Normalized email
        except EmailNotValidError as e:
            return False, f"Invalid email address: {str(e)}"

        # Get SMTP configuration from environment
        sender_email = os.getenv("GMAIL_SENDER_EMAIL")
        sender_password = os.getenv("GMAIL_APP_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        # Check for required credentials
        if not sender_email or not sender_password:
            return False, "Email configuration missing. Please set GMAIL_SENDER_EMAIL and GMAIL_APP_PASSWORD in .env file."

        # Generate PDF from analysis
        try:
            pdf_buffer = generate_pdf_from_analysis(analysis_text)
            pdf_bytes = pdf_buffer.getvalue()
        except Exception as e:
            return False, f"Failed to generate PDF: {str(e)}"

        # Parse analysis sections for email template
        sections = parse_analysis_sections(analysis_text)

        # Create email message
        message = MIMEMultipart('alternative')
        message['From'] = f"{sender_name or 'Home Inspection Analyzer'} <{sender_email}>"
        message['To'] = recipient_email
        message['Subject'] = "Your Home Inspection Analysis Report"

        # Render email templates
        html_body = render_html_email(
            critical_count=sections['critical_count'],
            important_count=sections['important_count'],
            minor_count=sections['minor_count'],
            overall_assessment=sections['overall_assessment'] or "See attached PDF for details.",
            recipient_name="there"
        )

        text_body = render_text_email(
            critical_count=sections['critical_count'],
            important_count=sections['important_count'],
            minor_count=sections['minor_count'],
            overall_assessment=sections['overall_assessment'] or "See attached PDF for details.",
            recipient_name="there"
        )

        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        message.attach(part1)
        message.attach(part2)

        # Attach PDF
        pdf_attachment = MIMEBase('application', 'pdf')
        pdf_attachment.set_payload(pdf_bytes)
        encoders.encode_base64(pdf_attachment)
        pdf_attachment.add_header(
            'Content-Disposition',
            'attachment',
            filename='home_inspection_analysis.pdf'
        )
        message.attach(pdf_attachment)

        # Send email via Gmail SMTP
        try:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
            server.ehlo()
            server.starttls()  # Secure connection
            server.ehlo()
            server.login(sender_email, sender_password)
            server.send_message(message)
            server.quit()

            return True, "Email sent successfully!"

        except smtplib.SMTPAuthenticationError:
            return False, "Gmail authentication failed. Please check your GMAIL_APP_PASSWORD in .env file. Make sure you're using an app password, not your regular Gmail password."

        except smtplib.SMTPRecipientsRefused:
            return False, f"Recipient email address was rejected: {recipient_email}"

        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"

        except TimeoutError:
            return False, "Connection to Gmail server timed out. Please check your internet connection."

        except ConnectionRefusedError:
            return False, "Connection to Gmail server refused. SMTP port may be blocked by firewall."

    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
