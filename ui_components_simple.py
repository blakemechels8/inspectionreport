"""
Simplified UI Components using Streamlit native elements
"""

import streamlit as st
from cost_parser import format_cost_range, format_currency, get_severity_level


def render_cost_summary_card_simple(cost_data):
    """Render cost summary using native Streamlit components"""

    totals = cost_data['totals']
    by_category = totals['by_category']

    # Create container with colored background
    with st.container():
        st.markdown("### 💰 ESTIMATED REPAIR COSTS")

        # Display total cost
        total_range = format_cost_range(totals['total_min'], totals['total_max'])
        st.markdown(f"<h1 style='text-align: center; color: #667eea;'>{total_range}</h1>",
                   unsafe_allow_html=True)

        # Severity badge
        severity = get_severity_level(totals['total_max'])
        severity_labels = {
            'low': ('LOW COST', '🟢'),
            'moderate': ('MODERATE COST', '🟡'),
            'high': ('HIGH COST', '🟠'),
            'very-high': ('VERY HIGH COST', '🔴')
        }
        label, icon = severity_labels.get(severity, severity_labels['moderate'])
        st.markdown(f"<h3 style='text-align: center;'>{icon} {label}</h3>",
                   unsafe_allow_html=True)

        st.markdown("---")

        # Cost breakdown
        st.markdown("#### COST BREAKDOWN BY PRIORITY")

        categories = [
            ('critical', '🔴 Critical'),
            ('important', '🟠 Important'),
            ('minor', '🔵 Minor')
        ]

        for category_key, category_label in categories:
            cat_data = by_category.get(category_key, {'min': 0, 'max': 0})
            if cat_data['max'] > 0:
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**{category_label}**")
                with col2:
                    st.write(format_cost_range(cat_data['min'], cat_data['max']))
                with col3:
                    percentage = (cat_data['max'] / totals['total_max']) * 100 if totals['total_max'] > 0 else 0
                    st.write(f"{int(percentage)}%")

                # Progress bar
                st.progress(percentage / 100)

        # Cost comparison
        if totals['total_max'] > 0:
            st.info(f"📊 This represents approximately {(totals['total_max'] / 300000) * 100:.1f}% of a typical $300k home purchase price")

        # Priority alert
        critical_data = by_category.get('critical', {'max': 0})
        if critical_data['max'] > 0:
            critical_percentage = (critical_data['max'] / totals['total_max']) * 100 if totals['total_max'] > 0 else 0
            if critical_percentage > 40:
                st.warning(f"⚠️ Critical issues represent {int(critical_percentage)}% of total costs and require immediate attention")


def render_detailed_cost_analysis_simple(cost_data):
    """Render detailed cost analysis using native Streamlit components"""

    totals = cost_data['totals']
    by_category = totals['by_category']

    st.markdown("---")
    st.markdown("## 📋 DETAILED COST ANALYSIS")

    # Cost breakdown table using st.dataframe or st.table
    st.markdown("### Cost Breakdown Table")

    import pandas as pd

    table_data = []
    categories = [
        ('critical', 'Critical', '🔴'),
        ('important', 'Important', '🟠'),
        ('minor', 'Minor', '🔵')
    ]

    for category_key, category_label, icon in categories:
        cat_data = by_category.get(category_key, {'min': 0, 'max': 0, 'count': 0, 'has_recurring': False})
        cost_type = 'Mixed' if cat_data.get('has_recurring') else 'One-time'

        table_data.append({
            'Category': f"{icon} {category_label}",
            'Min Cost': format_currency(cat_data['min']),
            'Max Cost': format_currency(cat_data['max']),
            '# Issues': cat_data['count'],
            'Type': cost_type
        })

    # Add total row
    table_data.append({
        'Category': '**TOTAL**',
        'Min Cost': f"**{format_currency(totals['total_min'])}**",
        'Max Cost': f"**{format_currency(totals['total_max'])}**",
        '# Issues': sum(cat['count'] for cat in by_category.values()),
        'Type': '—'
    })

    df = pd.DataFrame(table_data)
    st.table(df)

    # Priority recommendations
    st.markdown("### 🎯 Priority Recommendations")

    recommendations = []

    critical_data = by_category.get('critical', {'max': 0, 'min': 0})
    if critical_data['max'] > 0:
        recommendations.append(
            f"**1. Address critical issues first** ({format_cost_range(critical_data['min'], critical_data['max'])}) — These are safety hazards and structural problems that need immediate attention."
        )

    important_data = by_category.get('important', {'max': 0, 'min': 0})
    if important_data['max'] > 0:
        recommendations.append(
            f"**2. Schedule important repairs** ({format_cost_range(important_data['min'], important_data['max'])}) — Plan these within 6-12 months to prevent further deterioration."
        )

    minor_data = by_category.get('minor', {'max': 0, 'min': 0, 'count': 0})
    if minor_data['max'] > 0 and minor_data['count'] > 2:
        recommendations.append(
            f"**3. Bundle minor fixes** ({format_cost_range(minor_data['min'], minor_data['max'])}) — Combine {minor_data['count']} minor issues with a contractor for cost efficiency."
        )

    if recommendations:
        for rec in recommendations:
            st.markdown(rec)
    else:
        st.info("No cost estimates were found in the analysis. Review the detailed issues above for repair information.")

    # Cost-saving tips
    st.markdown("### 💡 Cost-Saving Tips")
    st.success("""
    - **Get multiple quotes:** Obtain at least 3 estimates for major repairs to ensure competitive pricing
    - **Negotiate purchase price:** Use repair costs to negotiate a lower price or request seller credits
    - **DIY where appropriate:** Some minor issues may be suitable for DIY if you have the skills
    - **Prioritize safety:** Focus budget on critical safety issues before cosmetic improvements
    - **Bundle repairs:** Combining multiple repairs with one contractor often reduces overall costs
    """)
