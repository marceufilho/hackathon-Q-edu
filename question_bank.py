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


class QuestionGenerator:
    """Base generator for all math questions"""

    @staticmethod
    def generate_basic_operations(difficulty: Difficulty = Difficulty.EASY) -> Dict:
        """
        Generate basic arithmetic operations questions

        Args:
            difficulty: Question difficulty level

        Returns:
            Dictionary with problem, solution, and metadata
        """
        operations = ['+', '-', '×', '÷']
        operation = random.choice(operations)

        if difficulty == Difficulty.EASY:
            a = random.randint(1, 20)
            b = random.randint(1, 10)
        elif difficulty == Difficulty.MEDIUM:
            a = random.randint(10, 50)
            b = random.randint(5, 25)
        else:  # HARD
            a = random.randint(20, 100)
            b = random.randint(10, 50)

        if operation == '+':
            answer = a + b
            problem = f"{a} + {b}"
            steps = [f"{a} + {b} = {answer}"]

        elif operation == '-':
            # Ensure positive result for EASY
            if difficulty == Difficulty.EASY and b > a:
                a, b = b, a
            answer = a - b
            problem = f"{a} - {b}"
            steps = [f"{a} - {b} = {answer}"]

        elif operation == '×':
            answer = a * b
            problem = f"{a} × {b}"
            steps = [f"{a} × {b} = {answer}"]

        else:  # ÷
            # Ensure divisibility
            answer = a
            a = a * b
            problem = f"{a} ÷ {b}"
            steps = [f"{a} ÷ {b} = {answer}"]

        return {
            "problem": f"Calcule: {problem}",
            "equation": problem,
            "answer": answer,
            "steps": steps,
            "difficulty": difficulty.value,
            "type": "basic_operations",
            "topic": "Operações Básicas"
        }

    @staticmethod
    def generate_integers(difficulty: Difficulty = Difficulty.EASY) -> Dict:
        """
        Generate questions about integers (positive and negative)

        Args:
            difficulty: Question difficulty level

        Returns:
            Dictionary with problem, solution, and metadata
        """
        question_type = random.choice(['addition', 'subtraction', 'comparison', 'absolute_value'])

        if difficulty == Difficulty.EASY:
            a = random.randint(-10, 10)
            b = random.randint(-10, 10)
        elif difficulty == Difficulty.MEDIUM:
            a = random.randint(-30, 30)
            b = random.randint(-30, 30)
        else:  # HARD
            a = random.randint(-100, 100)
            b = random.randint(-100, 100)

        if question_type == 'addition':
            answer = a + b
            problem = f"({a}) + ({b})"
            steps = [
                f"Somando números inteiros",
                f"({a}) + ({b}) = {answer}"
            ]

        elif question_type == 'subtraction':
            answer = a - b
            problem = f"({a}) - ({b})"
            steps = [
                f"Subtraindo números inteiros",
                f"({a}) - ({b}) = {answer}"
            ]

        elif question_type == 'comparison':
            problem = f"Qual é maior: {a} ou {b}?"
            answer = max(a, b)
            steps = [
                f"Comparando {a} e {b}",
                f"O maior é: {answer}"
            ]

        else:  # absolute_value
            problem = f"|{a}|"
            answer = abs(a)
            steps = [
                f"Valor absoluto de {a}",
                f"|{a}| = {answer}"
            ]

        return {
            "problem": f"Calcule: {problem}",
            "equation": problem,
            "answer": answer,
            "steps": steps,
            "difficulty": difficulty.value,
            "type": "integers",
            "topic": "Números Inteiros"
        }

    @staticmethod
    def generate_variables_expressions(difficulty: Difficulty = Difficulty.EASY) -> Dict:
        """
        Generate questions about variables and expressions

        Args:
            difficulty: Question difficulty level

        Returns:
            Dictionary with problem, solution, and metadata
        """
        if difficulty == Difficulty.EASY:
            coefficient = random.randint(2, 5)
            x_value = random.randint(1, 10)
            constant = random.randint(1, 10)
        elif difficulty == Difficulty.MEDIUM:
            coefficient = random.randint(2, 10)
            x_value = random.randint(-10, 10)
            constant = random.randint(-10, 10)
        else:  # HARD
            coefficient = random.randint(2, 15)
            x_value = random.randint(-20, 20)
            constant = random.randint(-20, 20)

        # Evaluate expression for given x
        expression = f"{coefficient}x + {constant}" if constant >= 0 else f"{coefficient}x - {abs(constant)}"
        answer = coefficient * x_value + constant

        problem = f"Avalie {expression} para x = {x_value}"
        steps = [
            f"Substitua x por {x_value}",
            f"{coefficient}({x_value}) + {constant}",
            f"{coefficient * x_value} + {constant}",
            f"{answer}"
        ]

        return {
            "problem": problem,
            "equation": expression,
            "answer": answer,
            "steps": steps,
            "difficulty": difficulty.value,
            "type": "variables_expressions",
            "topic": "Variáveis e Expressões"
        }

    @staticmethod
    def generate_algebraic_simplification(difficulty: Difficulty = Difficulty.MEDIUM) -> Dict:
        """
        Generate algebraic simplification questions

        Args:
            difficulty: Question difficulty level

        Returns:
            Dictionary with problem, solution, and metadata
        """
        if difficulty == Difficulty.EASY:
            a = random.randint(2, 5)
            b = random.randint(1, 5)
            c = random.randint(1, 5)
        elif difficulty == Difficulty.MEDIUM:
            a = random.randint(2, 10)
            b = random.randint(-10, 10)
            c = random.randint(-10, 10)
        else:  # HARD
            a = random.randint(2, 15)
            b = random.randint(-20, 20)
            c = random.randint(-20, 20)

        # Simplify ax + bx + c
        coefficient_sum = a + b

        term1 = f"{a}x"
        term2 = f"{b}x" if b >= 0 else f"- {abs(b)}x"
        term3 = f"+ {c}" if c >= 0 else f"- {abs(c)}"

        problem = f"{term1} + {term2} {term3}"

        if coefficient_sum == 0:
            simplified = str(c)
        elif c == 0:
            simplified = f"{coefficient_sum}x"
        else:
            simplified = f"{coefficient_sum}x + {c}" if c >= 0 else f"{coefficient_sum}x - {abs(c)}"

        steps = [
            f"Combine termos semelhantes",
            f"({a} + {b})x {term3}",
            f"{coefficient_sum}x {term3}",
            simplified
        ]

        return {
            "problem": f"Simplifique: {problem}",
            "equation": problem,
            "answer": simplified,
            "steps": steps,
            "difficulty": difficulty.value,
            "type": "algebraic_simplification",
            "topic": "Simplificação Algébrica"
        }

    @staticmethod
    def generate_inverse_operations(difficulty: Difficulty = Difficulty.EASY) -> Dict:
        """
        Generate questions about inverse operations

        Args:
            difficulty: Question difficulty level

        Returns:
            Dictionary with problem, solution, and metadata
        """
        operation_type = random.choice(['addition_inverse', 'multiplication_inverse'])

        if difficulty == Difficulty.EASY:
            num = random.randint(1, 20)
        elif difficulty == Difficulty.MEDIUM:
            num = random.randint(-30, 30)
        else:  # HARD
            num = random.randint(-100, 100)

        if operation_type == 'addition_inverse':
            problem = f"Qual é o inverso aditivo de {num}?"
            answer = -num
            steps = [
                f"O inverso aditivo é o número que, somado a {num}, resulta em 0",
                f"{num} + ({answer}) = 0",
                f"Resposta: {answer}"
            ]

        else:  # multiplication_inverse
            if num == 0:
                num = 1
            problem = f"Qual é o inverso multiplicativo de {num}?"

            # Return as fraction string
            if num == 1:
                answer = "1"
            elif num == -1:
                answer = "-1"
            else:
                answer = f"1/{num}" if num > 0 else f"-1/{abs(num)}"

            steps = [
                f"O inverso multiplicativo é o número que, multiplicado por {num}, resulta em 1",
                f"{num} × ({answer}) = 1",
                f"Resposta: {answer}"
            ]

        return {
            "problem": problem,
            "equation": str(num),
            "answer": answer,
            "steps": steps,
            "difficulty": difficulty.value,
            "type": "inverse_operations",
            "topic": "Operações Inversas"
        }


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
                f"Subtraia {constant} de ambos os lados",
                f"x = {b} - {constant}",
                f"x = {answer}"
            ]

        elif operation == 'subtract':
            # x - a = b
            b = answer - constant
            problem = f"x - {constant} = {b}"
            steps = [
                f"Adicione {constant} a ambos os lados",
                f"x = {b} + {constant}",
                f"x = {answer}"
            ]

        elif operation == 'multiply':
            # ax = b
            coefficient = random.randint(2, 10) if difficulty != Difficulty.HARD else random.randint(2, 20)
            b = answer * coefficient
            problem = f"{coefficient}x = {b}"
            steps = [
                f"Divida ambos os lados por {coefficient}",
                f"x = {b} / {coefficient}",
                f"x = {answer}"
            ]

        else:  # divide
            # x/a = b
            divisor = random.randint(2, 10) if difficulty != Difficulty.HARD else random.randint(2, 20)
            problem = f"x / {divisor} = {answer}"
            b = answer * divisor
            steps = [
                f"Multiplique ambos os lados por {divisor}",
                f"x = {answer} × {divisor}",
                f"x = {b}"
            ]
            answer = b

        return {
            "problem": f"Resolva para x: {problem}",
            "equation": problem,
            "answer": answer,
            "steps": steps,
            "difficulty": difficulty.value,
            "type": "one_step",
            "topic": "Equações Lineares"
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
            f"Subtraia {constant} de ambos os lados" if constant >= 0 else f"Adicione {abs(constant)} a ambos os lados",
            f"{coefficient}x = {c - constant}",
            f"Divida ambos os lados por {coefficient}",
            f"x = {(c - constant) / coefficient}",
            f"x = {answer}"
        ]

        return {
            "problem": f"Resolva para x: {problem}",
            "equation": problem,
            "answer": answer,
            "steps": steps,
            "difficulty": difficulty.value,
            "type": "two_step",
            "topic": "Equações Lineares"
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
            f"Subtraia {c}x de ambos os lados",
            f"{a - c}x + {b if b >= 0 else f'- {abs(b)}'} = {d}",
            f"Subtraia {b} de ambos os lados" if b >= 0 else f"Adicione {abs(b)} a ambos os lados",
            f"{a - c}x = {d - b}",
            f"Divida ambos os lados por {a - c}",
            f"x = {answer}"
        ]

        return {
            "problem": f"Resolva para x: {problem}",
            "equation": problem,
            "answer": answer,
            "steps": steps,
            "difficulty": difficulty.value,
            "type": "variables_both_sides",
            "topic": "Equações Lineares"
        }

    @staticmethod
    def generate_question(difficulty: Difficulty = None, question_type: str = None) -> Dict:
        """
        Generate a math question (supports all topics)

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

        # Linear equation types
        if question_type == 'one_step':
            return LinearEquationGenerator.generate_one_step(difficulty)
        elif question_type == 'two_step':
            return LinearEquationGenerator.generate_two_step(difficulty)
        elif question_type == 'variables_both_sides':
            return LinearEquationGenerator.generate_variables_both_sides(difficulty)

        # Prerequisite types
        elif question_type == 'basic_operations':
            return QuestionGenerator.generate_basic_operations(difficulty)
        elif question_type == 'integers':
            return QuestionGenerator.generate_integers(difficulty)
        elif question_type == 'variables_expressions':
            return QuestionGenerator.generate_variables_expressions(difficulty)
        elif question_type == 'algebraic_simplification':
            return QuestionGenerator.generate_algebraic_simplification(difficulty)
        elif question_type == 'inverse_operations':
            return QuestionGenerator.generate_inverse_operations(difficulty)

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
