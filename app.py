import streamlit as st
import pdfplumber
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from ui_components import (
    render_hero_section,
    render_progress_indicator,
    render_file_info_card,
    parse_and_display_analysis
)

# Page configuration
st.set_page_config(
    page_title="Home Inspection Analyzer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Custom CSS
st.markdown("""
<style>
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    /* Progress Indicator */
    .progress-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2.5rem 0;
        gap: 1rem;
    }

    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }

    .progress-circle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }

    .progress-step.active .progress-circle {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    .progress-label {
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .progress-line {
        width: 80px;
        height: 3px;
        border-radius: 2px;
        transition: all 0.3s ease;
    }

    /* Upload Section Card */
    .upload-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }

    /* File Info Card */
    .file-info-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }

    .file-info-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #dee2e6;
    }

    .file-info-row:last-child {
        border-bottom: none;
    }

    .file-info-label {
        font-weight: 600;
        color: #667eea;
    }

    .file-info-value {
        color: #1a1a1a;
        font-weight: 500;
    }

    /* Issue Cards */
    .critical-issue {
        background-color: #fff5f5;
        border-left: 5px solid #dc3545;
        border-radius: 12px;
        padding: 1.75rem;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(220, 53, 69, 0.15);
    }

    .important-issue {
        background-color: #fff8f0;
        border-left: 5px solid #ff9800;
        border-radius: 12px;
        padding: 1.75rem;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(255, 152, 0, 0.15);
    }

    .minor-issue {
        background-color: #f0f8ff;
        border-left: 5px solid #2196f3;
        border-radius: 12px;
        padding: 1.75rem;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.15);
    }

    .overall-assessment {
        background-color: #f0fff4;
        border-left: 5px solid #28a745;
        border-radius: 12px;
        padding: 1.75rem;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.15);
    }

    /* Severity Badges */
    .badge-high {
        background: #dc3545;
        color: white;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 2px 4px rgba(220, 53, 69, 0.3);
    }

    .badge-medium {
        background: #ff9800;
        color: white;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 2px 4px rgba(255, 152, 0, 0.3);
    }

    .badge-low {
        background: #2196f3;
        color: white;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 2px 4px rgba(33, 150, 243, 0.3);
    }

    /* Actions Section */
    .actions-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        margin-top: 2rem;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    /* Download Button */
    .stDownloadButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
    }

    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    /* Typography */
    h1, h2, h3 {
        color: #1a1a1a;
    }

    /* Success/Error Messages */
    .stSuccess, .stError, .stInfo {
        border-radius: 8px;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Cost Summary Card */
    .cost-summary-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
    }

    .cost-total {
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin: 1rem 0;
        letter-spacing: -0.5px;
    }

    /* Cost Chart */
    .cost-chart {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #1a1a1a;
    }

    .cost-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.25rem;
    }

    .cost-row:last-child {
        margin-bottom: 0;
    }

    .cost-bar {
        flex: 1;
        height: 32px;
        background: #e9ecef;
        border-radius: 16px;
        overflow: hidden;
    }

    .cost-bar-fill {
        height: 100%;
        border-radius: 16px;
        transition: width 0.6s ease;
    }

    /* Severity Badges */
    .cost-severity-low {
        background: #28a745;
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
    }

    .cost-severity-moderate {
        background: #ffc107;
        color: #000;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(255, 193, 7, 0.3);
    }

    .cost-severity-high {
        background: #ff9800;
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
    }

    .cost-severity-very-high {
        background: #dc3545;
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
    }

    /* Detailed Cost Card */
    .detailed-cost-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }

    /* Cost Table */
    .cost-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .cost-table th, .cost-table td {
        padding: 1rem;
        text-align: left;
        border-bottom: 1px solid #e9ecef;
    }

    .cost-table thead th {
        background: #667eea;
        color: white;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }

    .cost-table tbody tr:hover {
        background: #f8f9fa;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .progress-container {
            flex-direction: column;
            gap: 1.5rem;
        }

        .progress-line {
            width: 3px;
            height: 40px;
        }

        .hero {
            padding: 2rem 1rem;
        }

        .hero h1 {
            font-size: 1.8rem !important;
        }

        .cost-total {
            font-size: 2rem;
        }

        .cost-row {
            flex-wrap: wrap;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state['step'] = 1

# Hero Section
render_hero_section()

# Progress Indicator
render_progress_indicator(st.session_state['step'])

# Upload Section
st.markdown('<div class="upload-card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose your home inspection report (PDF)", type="pdf", label_visibility="visible")

if uploaded_file is not None:
    st.success("✅ PDF uploaded successfully!")
    st.session_state['step'] = max(st.session_state['step'], 1)

    # Show file details in styled card
    with pdfplumber.open(uploaded_file) as pdf:
        num_pages = len(pdf.pages)

    render_file_info_card(uploaded_file.name, uploaded_file.size / 1024, num_pages)

    # Extract text from PDF
    with st.spinner("Extracting text from PDF..."):
        with pdfplumber.open(uploaded_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"

    # Analyze button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔍 Analyze Report with AI", type="primary", use_container_width=True):
        st.session_state['step'] = 2
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Analysis Section
if st.session_state['step'] == 2 and uploaded_file is not None:
    with st.spinner("🤖 Claude is analyzing your inspection report... This may take 30-60 seconds."):
        # Call Claude API
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are an expert home inspector and contractor. Analyze this home inspection report and provide a clear, actionable summary for a homebuyer.

HOME INSPECTION REPORT:
{full_text}

Please provide:

1. **CRITICAL ISSUES (Must Address Immediately)** - Safety hazards, structural problems, or major system failures that need immediate attention. For each issue, provide:
   - Description of the problem
   - Why it's critical
   - Estimated cost range to fix

2. **IMPORTANT ISSUES (Should Address Soon)** - Items that aren't emergencies but should be fixed within 6-12 months. Include cost estimates.

3. **MINOR ISSUES (Low Priority)** - Normal wear and tear, cosmetic items, or things that can wait. Brief descriptions only.

4. **OVERALL ASSESSMENT** - A simple verdict: Is this home move-in ready, does it need work before moving in, or should the buyer walk away?

Be specific, use plain language, and focus on what a homebuyer actually needs to know."""
                }
            ]
        )

        # Store analysis
        analysis = message.content[0].text
        st.session_state['analysis'] = analysis
        st.session_state['step'] = 3
        st.rerun()

# Display Results
if 'analysis' in st.session_state and st.session_state['step'] == 3:
    st.markdown("---")
    st.markdown("## 📊 AI Analysis Results")

    # Parse costs and display summary card at top
    from cost_parser import parse_costs_from_analysis
    from ui_components_simple import render_cost_summary_card_simple, render_detailed_cost_analysis_simple

    cost_data = parse_costs_from_analysis(st.session_state['analysis'])

    # Display cost summary card at top
    render_cost_summary_card_simple(cost_data)

    st.markdown("Your inspection report has been analyzed. Review each section below:")
    st.markdown("<br>", unsafe_allow_html=True)

    # Display analysis in color-coded cards
    parse_and_display_analysis(st.session_state['analysis'])

    # Detailed cost analysis after issues
    render_detailed_cost_analysis_simple(cost_data)

    # Actions Section
    st.markdown("---")
    st.markdown("### 📥 Download or Email Your Report")
    st.markdown("Save or share the complete analysis")
    st.markdown("<br>", unsafe_allow_html=True)

    download_col, email_col = st.columns(2)

    with download_col:
        st.markdown("**📄 Download PDF Report**")
        st.write("Save the analysis to your device")

        try:
            from pdf_generator import generate_pdf_from_analysis
            from datetime import datetime

            pdf_buffer = generate_pdf_from_analysis(st.session_state['analysis'])
            pdf_bytes = pdf_buffer.getvalue()

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"home_inspection_analysis_{timestamp}.pdf"

            st.download_button(
                label="📄 Download PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")

    with email_col:
        st.markdown("**📧 Email Report**")
        st.write("Send the PDF to your email")

        recipient_email = st.text_input(
            "Email Address",
            placeholder="your-email@example.com",
            key="email_input",
            label_visibility="collapsed"
        )

        send_button = st.button("📤 Send Email", type="secondary", use_container_width=True)

        if send_button:
            if not recipient_email:
                st.error("Please enter an email address")
            else:
                with st.spinner("Sending email..."):
                    try:
                        from email_service import send_email_with_pdf

                        success, message = send_email_with_pdf(
                            recipient_email=recipient_email,
                            analysis_text=st.session_state['analysis']
                        )

                        if success:
                            st.success(f"✅ Sent to {recipient_email}!")
                            st.balloons()
                        else:
                            st.error(f"❌ {message}")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.info("Check your .env configuration")
