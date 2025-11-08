import os
import argparse
import google.generativeai as genai
from dotenv import load_dotenv
from math_solver import solve_math_problem
from parser import parse_solution
from confidence_score import calculate_confidence_score

def main():
    # Load environment variables
    load_dotenv()

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Q-Edu Math Solver - AI-powered step-by-step math problem solver',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py --problem "Solve for x: 2x + 5 = 15"
  python main.py -p "What is the derivative of x^2 + 3x?"
  python main.py --problem "Calculate the area of a circle with radius 5cm" --verbose
        '''
    )

    parser.add_argument(
        '-p', '--problem',
        type=str,
        required=True,
        help='The math problem to solve'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed output including confidence score'
    )

    args = parser.parse_args()

    # Get API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("GEMINI_API_KEY=your_key_here")
        return 1

    # Configure Gemini API
    genai.configure(api_key=api_key)

    print(f"\n{'='*60}")
    print(f"Q-Edu Math Solver")
    print(f"{'='*60}")
    print(f"\nProblem: {args.problem}\n")
    print("Thinking...\n")

    try:
        # Solve the problem
        solution_text = solve_math_problem(args.problem, api_key)

        # Parse the solution
        parsed = parse_solution(solution_text)

        # Display the solution
        if parsed['steps']:
            print("Step-by-Step Solution:")
            print("-" * 60)
            for i, step in enumerate(parsed['steps'], 1):
                print(f"\nStep {i}: {step}")
        else:
            print("Solution:")
            print("-" * 60)
            print(solution_text)

        # Display final answer
        if parsed['final_answer']:
            print(f"\n{'='*60}")
            print(f"Final Answer: {parsed['final_answer']}")
            print(f"{'='*60}")

        # Display confidence if verbose
        if args.verbose:
            if parsed['confidence']:
                print(f"\nConfidence Score: {parsed['confidence']}")
            else:
                # Calculate confidence if not in response
                confidence = calculate_confidence_score(solution_text, parsed['steps'])
                print(f"\nCalculated Confidence Score: {confidence:.2f}%")

        print("\n")
        return 0

    except Exception as e:
        print(f"\nError: An error occurred while solving the problem")
        print(f"Details: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
