"""
Question Bank for Linear Equations

Generates practice problems for linear equations with varying difficulty levels.
"""

import random
from typing import Dict, List
from enum import Enum


class Difficulty(Enum):
    """Difficulty levels for questions"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class LinearEquationGenerator:
    """Generates linear equation problems"""

    @staticmethod
    def generate_one_step(difficulty: Difficulty = Difficulty.EASY) -> Dict:
        """
        Generate one-step linear equations: x + a = b or ax = b

        Args:
            difficulty: Question difficulty level

        Returns:
            Dictionary with problem, solution, and metadata
        """
        # Choose operation type
        operation = random.choice(['add', 'subtract', 'multiply', 'divide'])

        if difficulty == Difficulty.EASY:
            answer = random.randint(1, 10)
            constant = random.randint(1, 10)
        elif difficulty == Difficulty.MEDIUM:
            answer = random.randint(-20, 20)
            constant = random.randint(-20, 20)
        else:  # HARD
            answer = random.randint(-50, 50)
            constant = random.randint(-50, 50)

        if operation == 'add':
            # x + a = b
            b = answer + constant
            problem = f"x + {constant} = {b}"
            steps = [
                f"Subtract {constant} from both sides",
                f"x = {b} - {constant}",
                f"x = {answer}"
            ]

        elif operation == 'subtract':
            # x - a = b
            b = answer - constant
            problem = f"x - {constant} = {b}"
            steps = [
                f"Add {constant} to both sides",
                f"x = {b} + {constant}",
                f"x = {answer}"
            ]

        elif operation == 'multiply':
            # ax = b
            coefficient = random.randint(2, 10) if difficulty != Difficulty.HARD else random.randint(2, 20)
            b = answer * coefficient
            problem = f"{coefficient}x = {b}"
            steps = [
                f"Divide both sides by {coefficient}",
                f"x = {b} / {coefficient}",
                f"x = {answer}"
            ]

        else:  # divide
            # x/a = b
            divisor = random.randint(2, 10) if difficulty != Difficulty.HARD else random.randint(2, 20)
            problem = f"x / {divisor} = {answer}"
            b = answer * divisor
            steps = [
                f"Multiply both sides by {divisor}",
                f"x = {answer} × {divisor}",
                f"x = {b}"
            ]
            answer = b

        return {
            "problem": f"Solve for x: {problem}",
            "equation": problem,
            "answer": answer,
            "steps": steps,
            "difficulty": difficulty.value,
            "type": "one_step",
            "topic": "Linear Equations"
        }

    @staticmethod
    def generate_two_step(difficulty: Difficulty = Difficulty.MEDIUM) -> Dict:
        """
        Generate two-step linear equations: ax + b = c

        Args:
            difficulty: Question difficulty level

        Returns:
            Dictionary with problem, solution, and metadata
        """
        if difficulty == Difficulty.EASY:
            answer = random.randint(1, 10)
            coefficient = random.randint(2, 5)
            constant = random.randint(1, 10)
        elif difficulty == Difficulty.MEDIUM:
            answer = random.randint(-20, 20)
            coefficient = random.randint(2, 10)
            constant = random.randint(-20, 20)
        else:  # HARD
            answer = random.randint(-50, 50)
            coefficient = random.randint(2, 15)
            constant = random.randint(-50, 50)

        # ax + b = c
        c = coefficient * answer + constant

        # Format with proper signs
        if constant >= 0:
            problem = f"{coefficient}x + {constant} = {c}"
        else:
            problem = f"{coefficient}x - {abs(constant)} = {c}"

        steps = [
            f"Subtract {constant} from both sides" if constant >= 0 else f"Add {abs(constant)} to both sides",
            f"{coefficient}x = {c - constant}",
            f"Divide both sides by {coefficient}",
            f"x = {(c - constant) / coefficient}",
            f"x = {answer}"
        ]

        return {
            "problem": f"Solve for x: {problem}",
            "equation": problem,
            "answer": answer,
            "steps": steps,
            "difficulty": difficulty.value,
            "type": "two_step",
            "topic": "Linear Equations"
        }

    @staticmethod
    def generate_variables_both_sides(difficulty: Difficulty = Difficulty.HARD) -> Dict:
        """
        Generate equations with variables on both sides: ax + b = cx + d

        Args:
            difficulty: Question difficulty level

        Returns:
            Dictionary with problem, solution, and metadata
        """
        if difficulty == Difficulty.MEDIUM:
            answer = random.randint(1, 15)
            a = random.randint(2, 5)
            c = random.randint(1, 4)
            b = random.randint(1, 10)
        else:  # HARD
            answer = random.randint(-30, 30)
            a = random.randint(2, 10)
            c = random.randint(1, 8)
            b = random.randint(-20, 20)

        # Make sure coefficients are different
        if a == c:
            c += 1

        # ax + b = cx + d
        # Solve for d: d = ax + b - cx = (a-c)x + b
        d = a * answer + b - c * answer

        # Format equation
        left = f"{a}x + {b}" if b >= 0 else f"{a}x - {abs(b)}"
        right = f"{c}x + {d}" if d >= 0 else f"{c}x - {abs(d)}"
        problem = f"{left} = {right}"

        steps = [
            f"Subtract {c}x from both sides",
            f"{a - c}x + {b if b >= 0 else f'- {abs(b)}'} = {d}",
            f"Subtract {b} from both sides" if b >= 0 else f"Add {abs(b)} to both sides",
            f"{a - c}x = {d - b}",
            f"Divide both sides by {a - c}",
            f"x = {answer}"
        ]

        return {
            "problem": f"Solve for x: {problem}",
            "equation": problem,
            "answer": answer,
            "steps": steps,
            "difficulty": difficulty.value,
            "type": "variables_both_sides",
            "topic": "Linear Equations"
        }

    @staticmethod
    def generate_question(difficulty: Difficulty = None, question_type: str = None) -> Dict:
        """
        Generate a linear equation question

        Args:
            difficulty: Question difficulty (random if None)
            question_type: Type of question (random if None)

        Returns:
            Dictionary with problem, solution, and metadata
        """
        if difficulty is None:
            difficulty = random.choice(list(Difficulty))

        if question_type is None:
            # Choose type based on difficulty
            if difficulty == Difficulty.EASY:
                question_type = 'one_step'
            elif difficulty == Difficulty.MEDIUM:
                question_type = random.choice(['one_step', 'two_step'])
            else:  # HARD
                question_type = random.choice(['two_step', 'variables_both_sides'])

        if question_type == 'one_step':
            return LinearEquationGenerator.generate_one_step(difficulty)
        elif question_type == 'two_step':
            return LinearEquationGenerator.generate_two_step(difficulty)
        elif question_type == 'variables_both_sides':
            return LinearEquationGenerator.generate_variables_both_sides(difficulty)
        else:
            raise ValueError(f"Unknown question type: {question_type}")

    @staticmethod
    def generate_batch(count: int = 10, difficulty: Difficulty = None) -> List[Dict]:
        """
        Generate a batch of questions

        Args:
            count: Number of questions to generate
            difficulty: Difficulty level (mixed if None)

        Returns:
            List of question dictionaries
        """
        questions = []
        for _ in range(count):
            question = LinearEquationGenerator.generate_question(difficulty)
            questions.append(question)
        return questions
