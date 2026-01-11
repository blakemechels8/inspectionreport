"""
Cost Parser Module
Extracts and analyzes cost estimates from home inspection analysis text
"""

import re


# Keywords to detect recurring costs
RECURRING_KEYWORDS = [
    'monthly', 'annual', 'annually', 'yearly', 'per month', 'per year',
    'ongoing', 'recurring', 'maintenance', 'subscription',
    'regular', 'continuous', 'periodic', 'each month', 'each year'
]


def extract_cost_ranges(text):
    """
    Extract dollar amounts from text in various formats

    Args:
        text: String containing cost mentions

    Returns:
        List of tuples (min_cost, max_cost, is_recurring)
    """
    costs = []

    # Pattern 1: Ranges like "$5,000-$8,000" or "$5k-$8k" or "between $5,000 and $8,000"
    # IMPORTANT: Also handle "$15,000-25,000" (dollar sign only on first number)
    # Work on original text (with commas) for better matching
    range_patterns = [
        r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*[-–]\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $15,000-25,000 or $15,000-$25,000
        r'\$(\d+(?:\.\d{2})?)\s*k\s*[-–]\s*\$?(\d+(?:\.\d{2})?)\s*k',  # $5k-$8k or $5k-8k
        r'between\s+\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s+and\s+\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # between $5,000 and $8,000
    ]

    for pattern in range_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)  # Work on original text WITH commas
        for match in matches:
            # Remove commas from matched numbers
            min_str = match.group(1).replace(',', '')
            max_str = match.group(2).replace(',', '')

            min_val = float(min_str)
            max_val = float(max_str)

            # Check if values are in thousands (k format)
            if 'k' in match.group(0).lower():
                min_val *= 1000
                max_val *= 1000

            # Detect if this is a recurring cost
            is_recurring = detect_recurring_costs(text[max(0, match.start()-50):min(len(text), match.end()+50)])

            costs.append((int(min_val), int(max_val), is_recurring))

    # Pattern 2: Single values like "$5,000" or "$5k"
    single_patterns = [
        r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*k(?![0-9])',  # $5k (not part of a range)
        r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)(?=\s|\.|\)|\]|$|[^0-9,.-])',  # $5,000 (not followed by k or range indicator)
    ]

    for pattern in single_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)  # Work on original text
        for match in matches:
            # Skip if this is part of a range we already captured
            skip = False
            for _ in costs:
                # Check if match position overlaps with existing matches
                # Simple check: if we already found costs, skip isolated numbers
                skip = True
                break

            if not skip:
                val_str = match.group(1).replace(',', '')
                val = float(val_str)

                # Check if value is in thousands (k format)
                if 'k' in match.group(0).lower():
                    val *= 1000

                # For single values, create a range with ±20% for estimate
                min_val = int(val * 0.8)
                max_val = int(val * 1.2)

                # Detect if this is a recurring cost
                is_recurring = detect_recurring_costs(text[max(0, match.start()-50):min(len(text), match.end()+50)])

                costs.append((min_val, max_val, is_recurring))

    return costs


def detect_recurring_costs(text):
    """
    Detect if a cost mention is recurring vs one-time

    Args:
        text: String to check for recurring keywords

    Returns:
        Boolean indicating if cost appears to be recurring
    """
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in RECURRING_KEYWORDS)


def categorize_costs(analysis_text):
    """
    Organize costs by section (critical, important, minor)

    Args:
        analysis_text: Full analysis markdown text from Claude

    Returns:
        Dict with costs categorized: {critical: [...], important: [...], minor: [...]}
    """
    categorized = {
        'critical': [],
        'important': [],
        'minor': []
    }

    # Extract sections using regex
    # Match both ## CRITICAL ISSUES and **CRITICAL ISSUES** formats
    critical_match = re.search(
        r'##\s*CRITICAL ISSUES.*?\n(.*?)(?=##\s*IMPORTANT ISSUES|##\s*MINOR ISSUES|##\s*OVERALL|$)',
        analysis_text, re.DOTALL | re.IGNORECASE
    )
    important_match = re.search(
        r'##\s*IMPORTANT ISSUES.*?\n(.*?)(?=##\s*MINOR ISSUES|##\s*OVERALL|$)',
        analysis_text, re.DOTALL | re.IGNORECASE
    )
    minor_match = re.search(
        r'##\s*MINOR ISSUES.*?\n(.*?)(?=##\s*OVERALL|$)',
        analysis_text, re.DOTALL | re.IGNORECASE
    )

    # Extract costs from each section
    if critical_match:
        categorized['critical'] = extract_cost_ranges(critical_match.group(1))

    if important_match:
        categorized['important'] = extract_cost_ranges(important_match.group(1))

    if minor_match:
        categorized['minor'] = extract_cost_ranges(minor_match.group(1))

    return categorized


def calculate_totals(categorized_costs):
    """
    Calculate total costs across all categories

    Args:
        categorized_costs: Dict from categorize_costs()

    Returns:
        Dict with totals: {total_min, total_max, by_category: {...}, has_recurring}
    """
    total_min = 0
    total_max = 0
    has_recurring = False
    by_category = {}

    for category, costs in categorized_costs.items():
        if not costs:
            by_category[category] = {
                'min': 0,
                'max': 0,
                'count': 0,
                'has_recurring': False
            }
            continue

        cat_min = sum(cost[0] for cost in costs)
        cat_max = sum(cost[1] for cost in costs)
        cat_recurring = any(cost[2] for cost in costs)

        by_category[category] = {
            'min': cat_min,
            'max': cat_max,
            'count': len(costs),
            'has_recurring': cat_recurring
        }

        total_min += cat_min
        total_max += cat_max

        if cat_recurring:
            has_recurring = True

    return {
        'total_min': total_min,
        'total_max': total_max,
        'by_category': by_category,
        'has_recurring': has_recurring
    }


def parse_costs_from_analysis(analysis_text):
    """
    Main function to parse and analyze costs from inspection analysis

    Args:
        analysis_text: Full analysis markdown text from Claude

    Returns:
        Dict with categorized costs and totals
    """
    categorized = categorize_costs(analysis_text)
    totals = calculate_totals(categorized)

    return {
        'categorized': categorized,
        'totals': totals
    }


def get_severity_level(total_cost_max):
    """
    Determine cost severity level based on maximum total cost

    Args:
        total_cost_max: Maximum total estimated cost

    Returns:
        String: "low", "moderate", "high", or "very-high"
    """
    if total_cost_max < 5000:
        return "low"
    elif total_cost_max < 15000:
        return "moderate"
    elif total_cost_max < 30000:
        return "high"
    else:
        return "very-high"


def format_currency(amount):
    """
    Format a number as currency

    Args:
        amount: Number to format

    Returns:
        Formatted string like "$5,000"
    """
    return f"${amount:,}"


def format_cost_range(min_cost, max_cost):
    """
    Format a cost range

    Args:
        min_cost: Minimum cost
        max_cost: Maximum cost

    Returns:
        Formatted string like "$5,000 - $8,000"
    """
    if min_cost == max_cost:
        return format_currency(min_cost)
    return f"{format_currency(min_cost)} - {format_currency(max_cost)}"
