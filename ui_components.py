"""
UI Components Module
Reusable visual components for the home inspection analyzer app
"""

import streamlit as st
import re


def render_hero_section():
    """Render the hero section with gradient background"""
    st.markdown("""
        <div class="hero">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">
                🏠 Home Inspection Report Analyzer
            </h1>
            <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">
                AI-Powered Analysis for Smarter Home Buying Decisions
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.85;">
                Upload your inspection report and get clear, actionable insights in minutes
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_progress_indicator(current_step):
    """
    Render progress indicator showing Upload -> Analyze -> Results

    Args:
        current_step: 1 (Upload), 2 (Analyzing), or 3 (Results)
    """
    steps = [
        {"num": 1, "label": "Upload", "icon": "📄"},
        {"num": 2, "label": "Analyze", "icon": "🔍"},
        {"num": 3, "label": "Results", "icon": "📊"}
    ]

    # Generate HTML for progress indicator
    html = '<div class="progress-container">'

    for i, step in enumerate(steps):
        # Determine step status
        if step["num"] < current_step:
            status = "completed"
            icon = "✓"
            color = "#28a745"
        elif step["num"] == current_step:
            status = "active"
            icon = step["icon"]
            color = "#667eea"
        else:
            status = "pending"
            icon = step["icon"]
            color = "#cccccc"

        # Add connector line (except for first step)
        if i > 0:
            line_color = "#28a745" if step["num"] <= current_step else "#e0e0e0"
            html += f'<div class="progress-line" style="background: {line_color};"></div>'

        # Add step circle
        html += f'''
            <div class="progress-step {status}">
                <div class="progress-circle" style="background: {color}; color: white;">
                    {icon}
                </div>
                <div class="progress-label" style="color: {color};">
                    {step["label"]}
                </div>
            </div>
        '''

    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)


def render_severity_badge(level):
    """
    Render a severity badge (HIGH/MEDIUM/LOW)

    Args:
        level: "high", "medium", or "low"

    Returns:
        HTML string for badge
    """
    badge_config = {
        "high": {"label": "HIGH PRIORITY", "class": "badge-high"},
        "medium": {"label": "MEDIUM PRIORITY", "class": "badge-medium"},
        "low": {"label": "LOW PRIORITY", "class": "badge-low"}
    }

    config = badge_config.get(level.lower(), badge_config["medium"])

    return f'<span class="{config["class"]}">{config["label"]}</span>'


def render_colored_issue_card(title, content, severity, icon=""):
    """
    Render a color-coded issue card

    Args:
        title: Card title
        content: Card content (HTML or text)
        severity: "critical", "important", or "minor"
        icon: Optional emoji icon
    """
    severity_class = f"{severity.lower()}-issue"
    badge_level = {"critical": "high", "important": "medium", "minor": "low"}.get(severity.lower(), "medium")
    badge_html = render_severity_badge(badge_level)

    html = f'''
        <div class="{severity_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; font-size: 1.3rem; font-weight: 600;">
                    {icon} {title}
                </h3>
                {badge_html}
            </div>
            <div class="issue-content">
                {content}
            </div>
        </div>
    '''

    st.markdown(html, unsafe_allow_html=True)


def render_file_info_card(filename, size, pages):
    """
    Render file information in a styled card

    Args:
        filename: Name of uploaded file
        size: File size in KB
        pages: Number of pages
    """
    html = f'''
        <div class="file-info-card">
            <div class="file-info-row">
                <span class="file-info-label">📄 Filename:</span>
                <span class="file-info-value">{filename}</span>
            </div>
            <div class="file-info-row">
                <span class="file-info-label">💾 File Size:</span>
                <span class="file-info-value">{size:.2f} KB</span>
            </div>
            <div class="file-info-row">
                <span class="file-info-label">📃 Pages:</span>
                <span class="file-info-value">{pages}</span>
            </div>
        </div>
    '''

    st.markdown(html, unsafe_allow_html=True)


def parse_and_display_analysis(analysis_text):
    """
    Parse Claude's markdown analysis and display in color-coded cards

    Args:
        analysis_text: Full analysis markdown text from Claude
    """
    # Extract sections using regex
    critical_match = re.search(
        r'\*\*CRITICAL ISSUES.*?\*\*(.*?)(?=\*\*IMPORTANT ISSUES|\*\*MINOR ISSUES|\*\*OVERALL ASSESSMENT|$)',
        analysis_text, re.DOTALL | re.IGNORECASE
    )
    important_match = re.search(
        r'\*\*IMPORTANT ISSUES.*?\*\*(.*?)(?=\*\*MINOR ISSUES|\*\*OVERALL ASSESSMENT|$)',
        analysis_text, re.DOTALL | re.IGNORECASE
    )
    minor_match = re.search(
        r'\*\*MINOR ISSUES.*?\*\*(.*?)(?=\*\*OVERALL ASSESSMENT|$)',
        analysis_text, re.DOTALL | re.IGNORECASE
    )
    overall_match = re.search(
        r'\*\*OVERALL ASSESSMENT.*?\*\*(.*?)$',
        analysis_text, re.DOTALL | re.IGNORECASE
    )

    # Display critical issues
    if critical_match:
        content = critical_match.group(1).strip()
        # Convert markdown to HTML for better display
        content_html = markdown_to_html(content)
        render_colored_issue_card(
            "CRITICAL ISSUES - Must Address Immediately",
            content_html,
            "critical",
            "🔴"
        )

    # Display important issues
    if important_match:
        content = important_match.group(1).strip()
        content_html = markdown_to_html(content)
        render_colored_issue_card(
            "IMPORTANT ISSUES - Should Address Soon",
            content_html,
            "important",
            "🟠"
        )

    # Display minor issues
    if minor_match:
        content = minor_match.group(1).strip()
        content_html = markdown_to_html(content)
        render_colored_issue_card(
            "MINOR ISSUES - Low Priority",
            content_html,
            "minor",
            "🔵"
        )

    # Display overall assessment
    if overall_match:
        content = overall_match.group(1).strip()
        content_html = markdown_to_html(content)

        # Determine if assessment is positive or negative
        negative_keywords = ["walk away", "not recommend", "serious concerns", "significant issues"]
        is_negative = any(keyword in content.lower() for keyword in negative_keywords)

        severity = "critical" if is_negative else "minor"  # Use blue/green for positive, red for negative

        html = f'''
            <div class="overall-assessment" style="border-left-color: {'#dc3545' if is_negative else '#28a745'};">
                <h3 style="margin: 0 0 1rem 0; font-size: 1.3rem; font-weight: 600;">
                    {'⚠️' if is_negative else '✅'} OVERALL ASSESSMENT
                </h3>
                <div class="assessment-content">
                    {content_html}
                </div>
            </div>
        '''

        st.markdown(html, unsafe_allow_html=True)


def markdown_to_html(text):
    """
    Convert simple markdown to HTML for display

    Args:
        text: Markdown formatted text

    Returns:
        HTML string
    """
    # Convert bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

    # Convert italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)

    # Convert line breaks to <br> for better spacing
    text = text.replace('\n\n', '<br><br>')
    text = text.replace('\n', '<br>')

    # Wrap in paragraph
    text = f'<div style="line-height: 1.6;">{text}</div>'

    return text


def render_cost_summary_card(cost_data):
    """
    Render cost summary card at top of results

    Args:
        cost_data: Cost data from cost_parser.parse_costs_from_analysis()
    """
    import streamlit as st
    from cost_parser import format_cost_range, get_severity_level

    totals = cost_data['totals']
    by_category = totals['by_category']

    # Debug output
    st.write("DEBUG: render_cost_summary_card called")

    # Determine severity
    severity = get_severity_level(totals['total_max'])
    severity_labels = {
        'low': 'LOW COST',
        'moderate': 'MODERATE COST',
        'high': 'HIGH COST',
        'very-high': 'VERY HIGH COST'
    }

    # Calculate percentages for chart
    total_max = totals['total_max'] if totals['total_max'] > 0 else 1  # Avoid division by zero

    # Calculate cost as percentage of typical home price ($300k)
    home_price = 300000
    cost_percentage = (totals['total_max'] / home_price) * 100 if totals['total_max'] > 0 else 0

    html = f'''
        <div class="cost-summary-card">
            <h2 style="margin: 0 0 1rem 0; font-size: 1.8rem; font-weight: 700; text-align: center;">
                💰 ESTIMATED REPAIR COSTS
            </h2>

            <div class="cost-total">
                {format_cost_range(totals['total_min'], totals['total_max'])}
            </div>

            <div style="text-align: center; margin-bottom: 2rem;">
                <span class="cost-severity-{severity}">{severity_labels[severity]}</span>
            </div>

            <div class="cost-breakdown-section">
                <h3 style="margin: 0 0 1rem 0; font-size: 1.1rem; font-weight: 600;">
                    COST BREAKDOWN BY PRIORITY
                </h3>

                <div class="cost-chart">
    '''

    # Add cost bars for each category
    categories = [
        ('critical', '🔴 Critical', '#dc3545'),
        ('important', '🟠 Important', '#ff9800'),
        ('minor', '🔵 Minor', '#2196f3')
    ]

    for category_key, category_label, color in categories:
        cat_data = by_category.get(category_key, {'min': 0, 'max': 0})
        if cat_data['max'] > 0:
            percentage = (cat_data['max'] / total_max) * 100
            html += f'''
                <div class="cost-row">
                    <div style="display: flex; align-items: center; gap: 0.5rem; min-width: 150px;">
                        <span style="font-weight: 600; color: #1a1a1a;">{category_label}</span>
                    </div>
                    <div style="min-width: 120px; text-align: right; font-weight: 500; color: #666;">
                        {format_cost_range(cat_data['min'], cat_data['max'])}
                    </div>
                    <div class="cost-bar">
                        <div class="cost-bar-fill" style="width: {percentage}%; background: {color};"></div>
                    </div>
                    <div style="min-width: 40px; text-align: right; font-weight: 600; color: {color};">
                        {int(percentage)}%
                    </div>
                </div>
            '''

    html += '''
                </div>
            </div>
    '''

    # Add cost comparison
    if totals['total_max'] > 0:
        html += f'''
            <div style="background: rgba(255,255,255,0.15); border-radius: 8px; padding: 1rem; margin-top: 1.5rem;">
                <p style="margin: 0; font-size: 0.95rem; opacity: 0.95;">
                    📊 This represents approximately <strong>{cost_percentage:.1f}%</strong> of a typical $300k home purchase price
                </p>
            </div>
        '''

    # Add priority alert if critical costs are significant
    critical_data = by_category.get('critical', {'max': 0})
    if critical_data['max'] > 0:
        critical_percentage = (critical_data['max'] / totals['total_max']) * 100 if totals['total_max'] > 0 else 0
        if critical_percentage > 40:
            html += f'''
                <div style="background: rgba(220, 53, 69, 0.2); border: 2px solid rgba(220, 53, 69, 0.5); border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                    <p style="margin: 0; font-size: 0.95rem; font-weight: 600;">
                        ⚠️ Critical issues represent {int(critical_percentage)}% of total costs and require immediate attention
                    </p>
                </div>
            '''

    # Add recurring cost notice
    if totals.get('has_recurring', False):
        html += '''
            <div style="background: rgba(255, 193, 7, 0.2); border: 2px solid rgba(255, 193, 7, 0.5); border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                <p style="margin: 0; font-size: 0.9rem; font-weight: 600;">
                    🔄 Some costs identified as recurring (ongoing maintenance or annual expenses)
                </p>
            </div>
        '''

    html += '</div>'

    st.write("DEBUG: About to render cost summary HTML, length:", len(html))
    try:
        st.markdown(html, unsafe_allow_html=True)
        st.write("DEBUG: Cost summary HTML rendered successfully")
    except Exception as e:
        st.error(f"ERROR rendering HTML: {e}")
        st.code(html[:500])  # Show first 500 chars


def render_detailed_cost_analysis(cost_data):
    """
    Render detailed cost analysis at bottom of results

    Args:
        cost_data: Cost data from cost_parser.parse_costs_from_analysis()
    """
    import streamlit as st
    from cost_parser import format_cost_range, format_currency

    # Debug output
    st.write("DEBUG: render_detailed_cost_analysis called")

    totals = cost_data['totals']
    by_category = totals['by_category']

    html = '''
        <div class="detailed-cost-card">
            <h2 style="margin: 0 0 1.5rem 0; font-size: 1.5rem; font-weight: 700; color: #1a1a1a;">
                📋 DETAILED COST ANALYSIS
            </h2>

            <h3 style="margin: 0 0 1rem 0; font-size: 1.2rem; font-weight: 600; color: #667eea;">
                Cost Breakdown Table
            </h3>

            <table class="cost-table">
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Min Cost</th>
                        <th>Max Cost</th>
                        <th># Issues</th>
                        <th>Type</th>
                    </tr>
                </thead>
                <tbody>
    '''

    # Add rows for each category
    categories = [
        ('critical', 'Critical', '🔴'),
        ('important', 'Important', '🟠'),
        ('minor', 'Minor', '🔵')
    ]

    for category_key, category_label, icon in categories:
        cat_data = by_category.get(category_key, {'min': 0, 'max': 0, 'count': 0, 'has_recurring': False})
        cost_type = 'Mixed' if cat_data.get('has_recurring') else 'One-time'

        html += f'''
            <tr>
                <td style="font-weight: 600;">{icon} {category_label}</td>
                <td>{format_currency(cat_data['min'])}</td>
                <td>{format_currency(cat_data['max'])}</td>
                <td>{cat_data['count']}</td>
                <td>{cost_type}</td>
            </tr>
        '''

    # Add total row
    html += f'''
                    <tr style="background: #f8f9fa; font-weight: 700; border-top: 2px solid #667eea;">
                        <td>TOTAL</td>
                        <td>{format_currency(totals['total_min'])}</td>
                        <td>{format_currency(totals['total_max'])}</td>
                        <td>{sum(cat['count'] for cat in by_category.values())}</td>
                        <td>—</td>
                    </tr>
                </tbody>
            </table>

            <div style="margin-top: 2rem;">
                <h3 style="margin: 0 0 1rem 0; font-size: 1.2rem; font-weight: 600; color: #667eea;">
                    🎯 Priority Recommendations
                </h3>
                <div style="background: #f8f9fa; border-left: 4px solid #667eea; border-radius: 8px; padding: 1.25rem;">
    '''

    # Generate priority recommendations
    recommendations = []

    critical_data = by_category.get('critical', {'max': 0})
    if critical_data['max'] > 0:
        recommendations.append(
            f"<strong>1. Address critical issues first</strong> ({format_cost_range(critical_data['min'], critical_data['max'])}) — These are safety hazards and structural problems that need immediate attention."
        )

    important_data = by_category.get('important', {'max': 0})
    if important_data['max'] > 0:
        recommendations.append(
            f"<strong>2. Schedule important repairs</strong> ({format_cost_range(important_data['min'], important_data['max'])}) — Plan these within 6-12 months to prevent further deterioration."
        )

    minor_data = by_category.get('minor', {'max': 0})
    if minor_data['max'] > 0 and minor_data['count'] > 2:
        recommendations.append(
            f"<strong>3. Bundle minor fixes</strong> ({format_cost_range(minor_data['min'], minor_data['max'])}) — Combine {minor_data['count']} minor issues with a contractor for cost efficiency."
        )

    if not recommendations:
        recommendations.append("No cost estimates were found in the analysis. Review the detailed issues above for repair information.")

    for rec in recommendations:
        html += f'<p style="margin: 0.75rem 0; line-height: 1.6;">{rec}</p>'

    html += '''
                </div>
            </div>

            <div style="margin-top: 2rem;">
                <h3 style="margin: 0 0 1rem 0; font-size: 1.2rem; font-weight: 600; color: #667eea;">
                    💡 Cost-Saving Tips
                </h3>
                <div style="background: #f0fff4; border-left: 4px solid #28a745; border-radius: 8px; padding: 1.25rem;">
                    <ul style="margin: 0; padding-left: 1.5rem; line-height: 1.8;">
                        <li><strong>Get multiple quotes:</strong> Obtain at least 3 estimates for major repairs to ensure competitive pricing</li>
                        <li><strong>Negotiate purchase price:</strong> Use repair costs to negotiate a lower price or request seller credits</li>
                        <li><strong>DIY where appropriate:</strong> Some minor issues may be suitable for DIY if you have the skills</li>
                        <li><strong>Prioritize safety:</strong> Focus budget on critical safety issues before cosmetic improvements</li>
                        <li><strong>Bundle repairs:</strong> Combining multiple repairs with one contractor often reduces overall costs</li>
                    </ul>
                </div>
            </div>
        </div>
    '''

    st.markdown(html, unsafe_allow_html=True)
