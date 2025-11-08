"""
Solution Generator

Generates step-by-step solutions for math problems using Google Gemini AI.
Provides detailed explanations and final answers for user-submitted questions.
"""

import google.generativeai as genai
from typing import Dict, List
import json


class SolutionGenerator:
    """Generate step-by-step solutions for math problems"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-thinking-exp-01-21"):
        """
        Initialize the solution generator

        Args:
            api_key: Google Gemini API key
            model_name: Model to use for solution generation
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_solution(self, problem: str) -> Dict:
        """
        Generate a complete step-by-step solution for a math problem

        Args:
            problem: The math problem to solve (e.g., "Solve for x: 2x + 5 = 13")

        Returns:
            Dictionary with:
            - problem: Original problem
            - answer: Final answer
            - steps: List of step-by-step explanations
            - concepts: Math concepts used in the solution
            - explanation: Overall explanation of the approach
        """
        prompt = self._build_solution_prompt(problem)

        try:
            response = self.model.generate_content(prompt)
            solution_data = self._parse_solution_response(response.text, problem)
            return solution_data

        except Exception as e:
            return {
                "problem": problem,
                "error": str(e),
                "answer": None,
                "steps": [],
                "concepts": [],
                "explanation": "Erro ao gerar solução. Por favor, tente novamente."
            }

    def _build_solution_prompt(self, problem: str) -> str:
        """
        Build the prompt for Gemini to generate step-by-step solution

        Args:
            problem: The math problem

        Returns:
            Complete prompt string
        """
        prompt = f"""
Você é um tutor de matemática experiente. Um estudante precisa de uma solução completa e detalhada para o seguinte problema:

**Problema:** {problem}

Por favor, forneça uma solução completa em PORTUGUÊS seguindo este formato EXATO em JSON:

{{
    "answer": "resposta final (apenas o valor, exemplo: x = 4 ou 42)",
    "steps": [
        "Passo 1: Descrição detalhada do primeiro passo",
        "Passo 2: Descrição detalhada do segundo passo",
        "Passo 3: Continue até resolver completamente"
    ],
    "concepts": [
        "Conceito matemático 1 usado",
        "Conceito matemático 2 usado"
    ],
    "explanation": "Breve explicação geral da abordagem usada para resolver este problema"
}}

**REQUISITOS IMPORTANTES:**
1. Retorne APENAS o JSON, sem texto adicional antes ou depois
2. Use português brasileiro em toda a resposta
3. Cada passo deve ser claro e educativo
4. Inclua todas as operações matemáticas realizadas
5. A resposta final deve ser clara e precisa
6. Liste todos os conceitos matemáticos relevantes
7. A explicação deve ser concisa (2-3 frases)

**EXEMPLO DE RESPOSTA:**
Se o problema for "Resolva para x: 2x + 5 = 13":
{{
    "answer": "x = 4",
    "steps": [
        "Passo 1: Subtraia 5 de ambos os lados da equação: 2x + 5 - 5 = 13 - 5",
        "Passo 2: Simplifique: 2x = 8",
        "Passo 3: Divida ambos os lados por 2: 2x / 2 = 8 / 2",
        "Passo 4: Simplifique para obter a resposta: x = 4"
    ],
    "concepts": [
        "Operações inversas",
        "Propriedade de igualdade",
        "Isolamento de variável"
    ],
    "explanation": "Para resolver uma equação linear, isolamos a variável aplicando operações inversas em ambos os lados da equação, mantendo a igualdade."
}}

Agora resolva o problema apresentado:
"""
        return prompt

    def _parse_solution_response(self, response_text: str, original_problem: str) -> Dict:
        """
        Parse the Gemini response to extract solution components

        Args:
            response_text: Raw text response from Gemini
            original_problem: The original problem

        Returns:
            Structured solution dictionary
        """
        try:
            # Try to extract JSON from the response
            # Sometimes Gemini wraps JSON in markdown code blocks
            text = response_text.strip()

            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]

            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

            # Parse JSON
            solution_data = json.loads(text)

            # Ensure all required fields exist
            result = {
                "problem": original_problem,
                "answer": solution_data.get("answer", "Não foi possível determinar"),
                "steps": solution_data.get("steps", []),
                "concepts": solution_data.get("concepts", []),
                "explanation": solution_data.get("explanation", "")
            }

            return result

        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract information manually
            return self._fallback_parse(response_text, original_problem)

    def _fallback_parse(self, response_text: str, original_problem: str) -> Dict:
        """
        Fallback parser when JSON parsing fails

        Args:
            response_text: Raw text response
            original_problem: Original problem

        Returns:
            Best-effort structured solution
        """
        lines = response_text.strip().split('\n')

        return {
            "problem": original_problem,
            "answer": "Ver explicação completa abaixo",
            "steps": [line.strip() for line in lines if line.strip()],
            "concepts": ["Matemática geral"],
            "explanation": "Solução completa fornecida acima."
        }

    def validate_problem(self, problem: str) -> tuple[bool, str]:
        """
        Validate that the input is a valid math problem

        Args:
            problem: Problem string to validate

        Returns:
            Tuple of (is_valid, message)
        """
        if not problem or len(problem.strip()) == 0:
            return False, "Problema vazio. Por favor, forneça um problema matemático."

        if len(problem) < 3:
            return False, "Problema muito curto. Por favor, forneça um problema completo."

        if len(problem) > 1000:
            return False, "Problema muito longo. Por favor, limite a 1000 caracteres."

        return True, "Problema válido"


def test_solution_generator():
    """Test function for solution generator"""
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("ERROR: GEMINI_API_KEY not found")
        return

    generator = SolutionGenerator(api_key)

    # Test problems
    test_problems = [
        "Resolva para x: 2x + 5 = 13",
        "Quanto é 15 + 23?",
        "Simplifique: 3x + 5x - 2x"
    ]

    for problem in test_problems:
        print(f"\n{'='*60}")
        print(f"Problema: {problem}")
        print('='*60)

        solution = generator.generate_solution(problem)

        print(f"\nResposta: {solution['answer']}")
        print(f"\nPassos:")
        for i, step in enumerate(solution['steps'], 1):
            print(f"  {i}. {step}")

        print(f"\nConceitos: {', '.join(solution['concepts'])}")
        print(f"\nExplicação: {solution['explanation']}")


if __name__ == "__main__":
    test_solution_generator()
