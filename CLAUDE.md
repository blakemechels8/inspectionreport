# Home Inspection Analyzer - AI Development Guide

This file contains lessons learned and patterns that work for this project. Read this before making changes.

## Critical Issues & Solutions

### Gmail App Password Setup (Time: 1+ hour)
**Problem:** Setting up Gmail to send emails is complex and error-prone.

**Solution Steps:**
1. Must enable 2-Factor Authentication on Google account FIRST
2. Go to https://myaccount.google.com/apppasswords
3. Create app password with custom name
4. Copy the 16-character password immediately
5. Add to Streamlit Secrets as: `GMAIL_APP_PASSWORD="your-password-here"`
6. Never use regular Gmail password - it won't work

**Common Error:** "Authentication failed" = wrong app password or 2FA not enabled

---

### Markdown/HTML Rendering in Streamlit (Time: 2+ hours)
**Problem:** Claude's analysis uses markdown formatting (headers with #, bold with **) which sometimes doesn't render correctly in Streamlit. Cost summaries disappeared because markdown symbols weren't being parsed properly.

**Root Cause:** 
- Using `st.write()` sometimes interprets markdown, sometimes doesn't
- Using `st.markdown()` is more reliable but has its own quirks
- Hashtags (#) in text can break section headers
- Mixed HTML and markdown causes rendering failures

**Solution:**
- ALWAYS use `st.markdown()` for displaying Claude's analysis
- Be consistent - don't mix `st.write()` and `st.markdown()` for the same content
- Test rendering after ANY change to display logic
- When extracting cost summaries, use regex/parsing on the RAW text BEFORE it's rendered

**Example that works:**
```python
st.markdown(analysis)  # For main display
# Extract costs from 'analysis' text directly, not from rendered output
```

---

### Cost Summary Regression Bug (Time: 1+ hour)
**Problem:** Cost summaries worked, then broke when removing a debugging message. Then had to fix it again for PDF and email outputs.

**What Happened:**
1. Initially cost summaries showed "$0" 
2. Fixed it for main display
3. Removed a debugging `st.write()` statement
4. Cost summaries reverted to "$0"
5. Fixed it again
6. PDF and email still showed "$0" because they used different code paths

**Root Cause:** The code had multiple places calculating/displaying costs:
- Main Streamlit display
- PDF generation
- Email body

Each needed the SAME cost extraction logic, but they were using different implementations.

**Solution:**
- Create ONE function that extracts costs from Claude's analysis
- Use that same function for display, PDF, and email
- Never duplicate the cost extraction logic
- When fixing bugs, check ALL output formats (screen, PDF, email)

**Code Pattern:**
```python
def extract_cost_summary(analysis_text):
    # Single source of truth for cost extraction
    # Parse the text and return structured cost data
    return total_cost

# Use everywhere:
total_cost = extract_cost_summary(analysis)
st.write(f"Total: {total_cost}")  # Display
# Use in PDF generation
# Use in email body
```

---

### Debugging Messages Breaking Production Code
**Problem:** Removing `st.write()` debugging statements sometimes breaks functionality.

**Why:** Streamlit reruns the entire script on every interaction. If your logic depends on session state or side effects from previous runs, removing a statement can change execution flow.

**Solution:**
- When adding debugging code, use comments like `# DEBUG - REMOVE BEFORE DEPLOY`
- Before removing debug code, test that the feature still works
- Use proper logging instead of `st.write()` for debugging
- Keep debug code in a separate branch/commit so you can revert easily

---

## Claude API Prompting - What Works

### Cost Estimation Prompt (DO NOT CHANGE)
The original prompt structure works perfectly. Modifications break cost extraction.

**Working prompt structure:**
```python
"""You are an expert home inspector and contractor. Analyze this home inspection report and provide a clear, actionable summary for a homebuyer.

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
```

**Key elements:**
- "expert home inspector and contractor" persona
- Explicit instruction: "Estimated cost range to fix"
- Format: "$X,XXX-$X,XXX" is what Claude outputs naturally
- DO NOT modify this prompt without testing cost extraction thoroughly

---

## Deployment Checklist

Before deploying to Streamlit Cloud:

- [ ] All new packages added to `requirements.txt`
- [ ] Environment variables added to Streamlit Secrets
- [ ] Test locally first (`python -m streamlit run app.py`)
- [ ] Test all output formats: screen, PDF, email
- [ ] Verify cost summaries show up everywhere
- [ ] Remove debugging `st.write()` statements carefully
- [ ] Commit changes with descriptive message
- [ ] Push to GitHub
- [ ] Verify deployment succeeds
- [ ] Test live site with real PDF

---

## Package Requirements

Current packages needed:
```
streamlit
pdfplumber
anthropic
python-dotenv
reportlab  # For PDF generation - MUST be in requirements.txt for deployment
```

---

## When Adding New Features

**Template prompt for Claude Code:**
```
I want to add [feature]. Before implementing:
1. What new packages will we need? (Add to requirements.txt)
2. Will this affect cost summary extraction? (Test all output formats)
3. Will this change how markdown renders? (Test with st.markdown())
4. What could go wrong?

Please implement with proper error handling.
```

---

## Common Pitfalls

❌ **Don't:** Remove debugging code without testing
❌ **Don't:** Modify the Claude API prompt without backing up the original
❌ **Don't:** Mix `st.write()` and `st.markdown()` for the same content
❌ **Don't:** Forget to add packages to requirements.txt
❌ **Don't:** Duplicate cost extraction logic in multiple places

✅ **Do:** Test all output formats after changes
✅ **Do:** Use one function for cost extraction
✅ **Do:** Add new packages to requirements.txt immediately
✅ **Do:** Test locally before deploying
✅ **Do:** Keep the original working prompt as a backup