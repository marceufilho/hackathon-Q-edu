def assess_step_clarity(steps):
    """Assess how clear and well-structured the reasoning steps are"""
    if not steps:
        return 0.5

    clarity_score = 0.0

    # Check for numbered or structured steps
    if len(steps) > 0:
        clarity_score += 0.3

    # Check if steps have reasonable length (not too short, not too long)
    avg_length = sum(len(step) for step in steps) / len(steps) if steps else 0
    if 20 < avg_length < 500:
        clarity_score += 0.3
    elif avg_length > 0:
        clarity_score += 0.1

    # Check for mathematical notation or formulas
    math_indicators = ['=', '+', '-', '*', '/', '^', '(', ')']
    for step in steps:
        if any(indicator in step for indicator in math_indicators):
            clarity_score += 0.4 / len(steps)

    return min(1.0, clarity_score)

def check_logical_flow(steps):
    """Check if the reasoning follows a logical progression"""
    if not steps:
        return 0.5

    flow_score = 0.0

    # Check if we have multiple steps (shows progression)
    if len(steps) >= 2:
        flow_score += 0.3

    # Check for logical connectors and progression words
    connectors = ['therefore', 'thus', 'so', 'then', 'next', 'because',
                  'since', 'as', 'consequently', 'hence']
    connector_count = sum(1 for step in steps
                         for connector in connectors
                         if connector in step.lower())
    if connector_count > 0:
        flow_score += min(0.4, connector_count * 0.1)

    # Check if steps build on each other (look for references to previous work)
    reference_words = ['from', 'using', 'substituting', 'applying', 'with']
    reference_count = sum(1 for step in steps
                         for word in reference_words
                         if word in step.lower())
    if reference_count > 0:
        flow_score += min(0.3, reference_count * 0.1)

    return min(1.0, flow_score)

def calculate_confidence_score(solution_text, steps=None):
    """Calculate confidence based on reasoning quality

    Args:
        solution_text: The full solution text from the model
        steps: Optional list of parsed steps

    Returns:
        Confidence score as a percentage (0-100)
    """
    # If no steps provided, treat the whole text as one step
    if not steps:
        steps = [solution_text]

    factors = {
        'step_clarity': assess_step_clarity(steps),
        'logical_consistency': check_logical_flow(steps),
        'has_content': 1.0 if solution_text and len(solution_text) > 20 else 0.3,
        'length_quality': min(1.0, len(solution_text) / 500) if solution_text else 0.0
    }

    # Weighted confidence calculation
    weights = {
        'step_clarity': 0.35,
        'logical_consistency': 0.35,
        'has_content': 0.15,
        'length_quality': 0.15
    }

    confidence = sum(factors[key] * weights[key] for key in factors)
    # Return as percentage
    return min(100.0, max(0.0, confidence * 100))