import google.generativeai as genai

def standard_solve(problem):
    """Solve using standard Gemini model for simple problems"""
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Solve this math problem clearly and concisely:
    {problem}

    Provide:
    1. Brief explanation
    2. Step-by-step solution
    3. Final answer
    """

    response = model.generate_content(prompt)
    return response.text

def deep_thinking_solve(problem):
    """Solve using deep thinking model for complex problems"""
    model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')

    prompt = f"""
    Solve this step by step, showing your reasoning:
    {problem}

    Use deep thinking mode to:
    1. Analyze the problem structure
    2. Plan your approach
    3. Execute calculations
    4. Verify your answer
    """

    response = model.generate_content(prompt)
    return response.text

def cost_optimized_solver(problem, complexity_level="auto"):
    """Smart routing based on problem complexity"""

    if complexity_level == "auto":
        complexity_level = assess_problem_complexity(problem)

    if complexity_level == "simple":
        # Use standard model for basic problems
        return standard_solve(problem)
    else:
        # Use deep thinking for complex problems
        return deep_thinking_solve(problem)

def assess_problem_complexity(problem):
    """Simple heuristic to assess problem complexity"""
    complexity_indicators = [
        "derivative", "integral", "limit", "proof",
        "optimization", "differential equation",
        "series", "matrix", "eigenvector", "polynomial",
        "logarithm", "exponential", "trigonometric"
    ]

    indicator_count = sum(1 for indicator in complexity_indicators
                         if indicator in problem.lower())

    # Also check for multiple operations or long problems
    operation_count = problem.count('+') + problem.count('-') + problem.count('*') + problem.count('/')
    word_count = len(problem.split())

    # Complex if: has 2+ complexity indicators OR (has indicator AND many operations/long)
    if indicator_count >= 2:
        return "complex"
    elif indicator_count >= 1 and (operation_count > 5 or word_count > 20):
        return "complex"
    else:
        return "simple"