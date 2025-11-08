def parse_solution(response):
    """Extract structured data from AI response"""
    lines = response.split('\n')
    solution_data = {
        'steps': [],
        'final_answer': None,
        'confidence': None
    }
    
    # Parse response structure
    current_step = ""
    for line in lines:
        if line.startswith("Step"):
            if current_step:
                solution_data['steps'].append(current_step)
            current_step = line
        elif "Final Answer:" in line:
            solution_data['final_answer'] = line.replace("Final Answer:", "").strip()
        elif current_step:
            current_step += f"\n{line}"
    
    return solution_data