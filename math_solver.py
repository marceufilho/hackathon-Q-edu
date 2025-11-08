import google.generativeai as genai

def solve_math_problem(problem, api_key=None):
    if api_key:
        genai.configure(api_key=api_key)

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