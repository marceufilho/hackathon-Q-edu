"""
Socratic Math Teacher

Core teaching logic that uses Polya's method with Socratic questioning
to guide students through problem solving without giving direct answers.
"""

import os
import google.generativeai as genai
from typing import Dict, List, Optional
from polya_phases import PolyaPhase, PhaseConfig, PhaseTransition
from hint_system import HintLevel, HintEscalation, HintTemplates


class SocraticTeacher:
    """
    AI-powered Socratic teacher for mathematics using Polya's method
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Socratic teacher

        Args:
            api_key: Google Gemini API key (if not provided, reads from env)
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')

    def generate_initial_question(self, problem: str) -> str:
        """
        Generate the first Socratic question to start the teaching session

        Args:
            problem: The math problem to solve

        Returns:
            The first question to ask the student
        """
        phase = PolyaPhase.UNDERSTANDING
        phase_config = PhaseConfig.get_phase_config(phase)

        prompt = self._build_prompt(
            problem=problem,
            phase=phase,
            hint_level=HintLevel.GENTLE,
            conversation_history=[],
            is_first_question=True
        )

        response = self.model.generate_content(prompt)
        return response.text.strip()

    def generate_next_question(
        self,
        problem: str,
        current_phase: PolyaPhase,
        hint_level: HintLevel,
        conversation_history: List[Dict],
        student_response: str
    ) -> Dict:
        """
        Generate the next Socratic question based on student's response

        Args:
            problem: The original math problem
            current_phase: Current Polya phase
            hint_level: Current hint level
            conversation_history: Previous conversation exchanges
            student_response: Student's latest response

        Returns:
            Dictionary with:
                - question: The next question to ask
                - phase: Current or next phase
                - hint_level: Current hint level
                - should_advance: Whether phase should advance
                - is_complete: Whether all phases are complete
        """
        # Check if we should advance to the next phase
        should_advance = PhaseTransition.should_advance_phase(
            current_phase, conversation_history, student_response
        )

        next_phase = current_phase
        if should_advance and not PhaseTransition.is_complete(current_phase):
            next_phase = PhaseTransition.get_next_phase(current_phase)

        # Build the prompt
        prompt = self._build_prompt(
            problem=problem,
            phase=next_phase,
            hint_level=hint_level,
            conversation_history=conversation_history,
            student_response=student_response,
            is_first_question=False
        )

        # Generate the next question
        response = self.model.generate_content(prompt)
        question = response.text.strip()

        # Check if all phases are complete
        is_complete = (next_phase == PolyaPhase.REVIEW and
                      len(conversation_history) >= 8)  # Minimum exchanges

        return {
            "question": question,
            "phase": next_phase,
            "hint_level": hint_level,
            "should_advance": should_advance,
            "is_complete": is_complete
        }

    def _build_prompt(
        self,
        problem: str,
        phase: PolyaPhase,
        hint_level: HintLevel,
        conversation_history: List[Dict],
        student_response: str = None,
        is_first_question: bool = False
    ) -> str:
        """
        Build the prompt for the LLM based on context

        Args:
            problem: The math problem
            phase: Current Polya phase
            hint_level: Current hint level
            conversation_history: Previous exchanges
            student_response: Latest student response
            is_first_question: Whether this is the first question

        Returns:
            Formatted prompt for the LLM
        """
        phase_config = PhaseConfig.get_phase_config(phase)
        phase_name = phase_config["name"]
        hint_guidance = HintTemplates.get_hint_guidance(hint_level, phase_name)

        # Base system instructions
        system_instructions = f"""Você é um professor de matemática socrático usando o método de resolução de problemas de Polya.

REGRAS CRÍTICAS:
1. NUNCA dê respostas ou soluções diretas
2. NUNCA resolva o problema para o estudante
3. SEMPRE faça perguntas que guiem o estudante a descobrir a resposta por si mesmo
4. Use o método socrático: faça perguntas investigativas, encoraje o pensamento
5. Seja paciente, encorajador e solidário
6. Mantenha respostas concisas (máximo 2-3 frases)
7. SEMPRE responda em português brasileiro

FASE ATUAL: {phase_name}
{phase_config["description"]}

Objetivos da Fase:
{chr(10).join(f"- {goal}" for goal in phase_config["goals"])}

{hint_guidance}

PROBLEMA PARA RESOLVER:
{problem}
"""

        # Add conversation history if available
        if conversation_history:
            history_text = "\n\nCONVERSA ATÉ AGORA:\n"
            for i, exchange in enumerate(conversation_history[-5:], 1):  # Last 5 exchanges
                history_text += f"\nProfessor: {exchange.get('question', '')}\n"
                history_text += f"Estudante: {exchange.get('response', '')}\n"
            system_instructions += history_text

        # Add current student response if provided
        if student_response and not is_first_question:
            system_instructions += f"\n\nÚLTIMA RESPOSTA DO ESTUDANTE:\n{student_response}\n"
            system_instructions += "\nCom base nesta resposta, faça a próxima pergunta socrática para guiá-lo adiante."

        # First question instruction
        if is_first_question:
            system_instructions += f"\n\nGere a PRIMEIRA pergunta socrática para iniciar a fase '{phase_name}'."
            system_instructions += f"\nEscolha uma dessas perguntas iniciais ou crie uma similar:\n"
            for starter in phase_config["socratic_starters"][:3]:
                system_instructions += f"- {starter}\n"

        return system_instructions

    def evaluate_student_response(
        self,
        problem: str,
        student_response: str,
        expected_understanding: str = None
    ) -> Dict:
        """
        Evaluate if student's response shows understanding
        (Used for adaptive hint escalation)

        Args:
            problem: The math problem
            student_response: Student's response
            expected_understanding: What we expect them to understand

        Returns:
            Dictionary with evaluation results
        """
        # Simple evaluation - in production, could use LLM for more sophisticated analysis
        response_lower = student_response.lower()

        # Basic heuristics
        shows_math = any(c in student_response for c in "=+-*/()x")
        is_substantial = len(student_response.split()) > 3
        not_confused = not any(word in response_lower
                              for word in ["don't know", "confused", "stuck"])

        return {
            "shows_understanding": shows_math and is_substantial and not_confused,
            "needs_help": not (shows_math or is_substantial) or not not_confused,
            "confidence": "high" if shows_math and is_substantial else "low"
        }
