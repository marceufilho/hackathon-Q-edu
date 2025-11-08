"""
Example Client for Q-Edu Socratic Math Teacher API

Demonstrates how to interact with the teaching API to guide a student
through solving a linear equation using Polya's method.
"""

import requests
import json
import time

# API Configuration
API_BASE_URL = "http://localhost:5000"


def print_separator():
    """Print a visual separator"""
    print("\n" + "=" * 70)


def print_teacher(message, phase=None, hint_level=None):
    """Print teacher's message with formatting"""
    prefix = "Teacher"
    if phase or hint_level is not None:
        details = []
        if phase:
            details.append(f"Phase: {phase}")
        if hint_level is not None:
            details.append(f"Hint Level: {hint_level}")
        prefix += f" [{', '.join(details)}]"

    print(f"\n{prefix}:")
    print(f"  {message}")


def print_student(message):
    """Print student's message with formatting"""
    print(f"\nStudent:")
    print(f"  {message}")


def start_session(problem):
    """
    Start a new teaching session

    Args:
        problem: The math problem to solve

    Returns:
        Session data with session_id and first question
    """
    print_separator()
    print("STARTING NEW TEACHING SESSION")
    print_separator()
    print(f"\nProblem: {problem}")

    response = requests.post(
        f"{API_BASE_URL}/start",
        json={"problem": problem}
    )

    if response.status_code == 201:
        session = response.json()
        print(f"\nSession ID: {session['session_id']}")
        print_teacher(
            session['question'],
            phase=session['phase'],
            hint_level=session['hint_level']
        )
        return session
    else:
        print(f"\nError starting session: {response.json()}")
        return None


def submit_response(session_id, student_response):
    """
    Submit a student response and get next question

    Args:
        session_id: The session identifier
        student_response: Student's answer

    Returns:
        Response data with next question
    """
    print_student(student_response)

    response = requests.post(
        f"{API_BASE_URL}/respond",
        json={
            "session_id": session_id,
            "response": student_response
        }
    )

    if response.status_code == 200:
        result = response.json()

        if result.get("encouragement"):
            print(f"\n  [{result['encouragement']}]")

        print_teacher(
            result['question'],
            phase=result.get('phase'),
            hint_level=result.get('hint_level')
        )

        if result.get('is_complete'):
            print_separator()
            print("SESSION COMPLETE!")
            print_separator()
            if result.get('message'):
                print(f"\n{result['message']}")

        return result
    else:
        print(f"\nError submitting response: {response.json()}")
        return None


def get_session_details(session_id):
    """
    Retrieve full session details

    Args:
        session_id: The session identifier

    Returns:
        Full session data
    """
    response = requests.get(f"{API_BASE_URL}/session/{session_id}")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"\nError getting session: {response.json()}")
        return None


def run_interactive_demo():
    """
    Run an interactive demo where you can play as the student
    """
    print("\n" + "=" * 70)
    print(" Q-EDU SOCRATIC MATH TEACHER - INTERACTIVE DEMO")
    print("=" * 70)

    problem = input("\nEnter a math problem (or press Enter for default): ").strip()
    if not problem:
        problem = "Solve for x: 2x + 5 = 13"

    session = start_session(problem)
    if not session:
        return

    session_id = session['session_id']

    while True:
        student_input = input("\nYour response (or 'quit' to exit): ").strip()

        if student_input.lower() in ['quit', 'exit', 'q']:
            print("\nEnding session...")
            break

        if not student_input:
            print("Please enter a response")
            continue

        result = submit_response(session_id, student_input)

        if result and result.get('is_complete'):
            break

        time.sleep(0.5)  # Small delay for readability

    # Show final session summary
    print_separator()
    print("SESSION SUMMARY")
    print_separator()

    details = get_session_details(session_id)
    if details:
        print(f"\nProblem: {details['problem']}")
        print(f"Final Phase: {details['current_phase']}")
        print(f"Total Exchanges: {len([m for m in details['conversation'] if m['role'] == 'student'])}")
        print(f"Completed: {'Yes' if details['is_complete'] else 'No'}")


def run_automated_demo():
    """
    Run an automated demo with pre-scripted responses
    """
    print("\n" + "=" * 70)
    print(" Q-EDU SOCRATIC MATH TEACHER - AUTOMATED DEMO")
    print("=" * 70)

    # Start session
    problem = "Solve for x: 2x + 5 = 13"
    session = start_session(problem)

    if not session:
        return

    session_id = session['session_id']

    # Pre-scripted conversation demonstrating Polya's method
    responses = [
        "The value of x",
        "We know that 2x + 5 equals 13",
        "We could subtract 5 from both sides",
        "2x = 8",
        "Divide both sides by 2",
        "x = 4",
        "Substitute 4 back into the original equation",
        "2(4) + 5 = 8 + 5 = 13, so it's correct!"
    ]

    for i, response in enumerate(responses, 1):
        time.sleep(1.5)  # Pause between exchanges for readability

        result = submit_response(session_id, response)

        if result and result.get('is_complete'):
            break

    # Show session summary
    print_separator()
    print("SESSION SUMMARY")
    print_separator()

    details = get_session_details(session_id)
    if details:
        print(f"\nProblem: {details['problem']}")
        print(f"Final Phase: {details['current_phase']}")
        print(f"Total Exchanges: {len([m for m in details['conversation'] if m['role'] == 'student'])}")
        print(f"Phases Visited:")
        phases_seen = set(m.get('phase') for m in details['conversation']
                         if m['role'] == 'teacher' and m.get('phase'))
        for phase in sorted(phases_seen):
            print(f"  - {phase}")


def run_struggle_demo():
    """
    Demo showing hint escalation when student struggles
    """
    print("\n" + "=" * 70)
    print(" Q-EDU - HINT ESCALATION DEMO")
    print("=" * 70)

    problem = "Solve for x: 3x - 7 = 11"
    session = start_session(problem)

    if not session:
        return

    session_id = session['session_id']

    # Responses showing struggle, triggering hint escalation
    responses = [
        "Find x",                    # Good start
        "I'm not sure",              # Struggle - escalates hint
        "Umm...",                    # More struggle - more directive
        "18 divided by 3",           # Following directive hint
        "x = 6",                     # Solution
        "Plug it back in",           # Verification
        "3(6) - 7 = 18 - 7 = 11"   # Verification complete
    ]

    for response in responses:
        time.sleep(1.5)

        result = submit_response(session_id, response)

        if result and result.get('is_complete'):
            break


def main():
    """Main entry point"""
    print("\nQ-Edu Socratic Math Teacher - Example Client")
    print("=" * 70)
    print("\nMake sure the API server is running:")
    print("  uv run python app.py")
    print("\nThen choose a demo mode:\n")
    print("1. Automated Demo (pre-scripted conversation)")
    print("2. Interactive Demo (you play as student)")
    print("3. Hint Escalation Demo (shows adaptive hints)")
    print("4. Exit")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        run_automated_demo()
    elif choice == "2":
        run_interactive_demo()
    elif choice == "3":
        run_struggle_demo()
    elif choice == "4":
        print("\nGoodbye!")
        return
    else:
        print("\nInvalid choice")
        return

    print("\n" + "=" * 70)
    print("\nDemo complete! Check the sessions/ directory to see saved data.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
