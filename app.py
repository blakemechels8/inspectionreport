import streamlit as st
import pdfplumber
from anthropic import Anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

st.title("Home Inspection Report Analyzer")
st.write("Upload your home inspection report PDF to get a clear analysis of what matters most.")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.success("✅ PDF uploaded successfully!")
    
    # Show file details
    st.write(f"**Filename:** {uploaded_file.name}")
    st.write(f"**File size:** {uploaded_file.size / 1024:.2f} KB")
    
    # Extract text from PDF
    with st.spinner("Extracting text from PDF..."):
        with pdfplumber.open(uploaded_file) as pdf:
            num_pages = len(pdf.pages)
            st.write(f"**Total pages:** {num_pages}")
            
            # Extract text from all pages
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
    
    # Analyze button
    if st.button("🔍 Analyze Report with AI", type="primary"):
        with st.spinner("Claude is analyzing your inspection report... This may take 30-60 seconds."):
            
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
            
            # Display the analysis
            analysis = message.content[0].text
            
            st.markdown("---")
            st.markdown("## 📊 AI Analysis Results")
            st.markdown(analysis)
            
            # Store in session state
            st.session_state['analysis'] = analysis
            