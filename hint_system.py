"""
Hint Escalation System

Implements a 3-level hint system that escalates from gentle Socratic questions
to more directive guidance when students struggle.

Levels:
- Level 0 (Gentle): Open-ended Socratic questions
- Level 1 (Specific): Pointed questions with context
- Level 2 (Directive): Almost-answer level guidance
"""

from enum import IntEnum
from typing import List, Dict


class HintLevel(IntEnum):
    """Hint escalation levels"""
    GENTLE = 0      # Open-ended Socratic questions
    SPECIFIC = 1    # Pointed questions with context
    DIRECTIVE = 2   # Very explicit guidance


class StruggleDetector:
    """Detects when a student is struggling and needs more help"""

    STRUGGLE_INDICATORS = [
        "não sei",
        "não tenho certeza",
        "estou preso",
        "estou travado",
        "não entendo",
        "estou confuso",
        "sem ideia",
        "pode me ajudar",
        "me ajuda",
        "desisto",
        "o que eu faço",
        "não consigo",
        "não sei como",
        "i don't know",
        "i'm not sure",
        "i'm stuck",
        "i don't understand"
    ]

    VAGUE_RESPONSES = [
        "sei lá",
        "tipo",
        "né",
        "hmm",
        "talvez",
        "acho que",
        "não sei bem",
        "idk",
        "umm"
    ]

    @staticmethod
    def is_struggling(response: str) -> bool:
        """
        Detect if student response indicates struggle

        Args:
            response: Student's response text

        Returns:
            True if struggling, False otherwise
        """
        response_lower = response.lower().strip()

        # Check for explicit struggle indicators
        for indicator in StruggleDetector.STRUGGLE_INDICATORS:
            if indicator in response_lower:
                return True

        # Check for very short vague responses
        if len(response_lower) < 10:
            for vague in StruggleDetector.VAGUE_RESPONSES:
                if response_lower.startswith(vague):
                    return True

        # Empty or very short response
        if len(response_lower) < 3:
            return True

        return False

    @staticmethod
    def is_incorrect(response: str, expected_pattern: str = None) -> bool:
        """
        Basic check if response seems incorrect
        (This is a simple heuristic - can be enhanced)

        Args:
            response: Student's response
            expected_pattern: Optional pattern to match against

        Returns:
            True if likely incorrect, False otherwise
        """
        # This is a placeholder - in practice, we'd use the LLM to evaluate
        # For now, just flag very short or vague responses as potentially incorrect
        response_lower = response.lower().strip()

        if len(response_lower) < 2:
            return True

        return False


class HintEscalation:
    """Manages hint level escalation based on student struggles"""

    def __init__(self):
        self.current_level = HintLevel.GENTLE
        self.struggle_count = 0
        self.consecutive_struggles = 0

    def update_from_response(self, student_response: str, was_helpful: bool = None) -> HintLevel:
        """
        Update hint level based on student's response

        Args:
            student_response: The student's latest response
            was_helpful: Optional flag indicating if response shows progress

        Returns:
            The updated hint level
        """
        is_struggling = StruggleDetector.is_struggling(student_response)

        if is_struggling:
            self.struggle_count += 1
            self.consecutive_struggles += 1
            self._escalate()
        else:
            # Student seems to be making progress
            self.consecutive_struggles = 0
            # Don't de-escalate immediately, but stop escalating
            if self.struggle_count > 0:
                self.struggle_count = max(0, self.struggle_count - 1)

        return self.current_level

    def _escalate(self):
        """Escalate hint level based on struggle count"""
        if self.consecutive_struggles >= 2:
            # After 2 consecutive struggles, move to directive
            self.current_level = HintLevel.DIRECTIVE
        elif self.consecutive_struggles >= 1:
            # After 1 struggle, move to specific
            self.current_level = min(HintLevel.SPECIFIC, self.current_level + 1)

    def reset(self):
        """Reset to gentle hints (e.g., when moving to new phase)"""
        self.current_level = HintLevel.GENTLE
        self.struggle_count = 0
        self.consecutive_struggles = 0

    def get_level(self) -> HintLevel:
        """Get current hint level"""
        return self.current_level

    def get_level_name(self) -> str:
        """Get human-readable name of current level"""
        return self.current_level.name.title()


class HintTemplates:
    """Templates for generating hints at different levels"""

    @staticmethod
    def get_hint_guidance(level: HintLevel, phase_name: str) -> str:
        """
        Get guidance text to include in prompts for the LLM

        Args:
            level: Current hint level
            phase_name: Current Polya phase name

        Returns:
            Guidance text for the LLM
        """
        if level == HintLevel.GENTLE:
            return f"""
Você está na fase "{phase_name}". Faça perguntas socráticas abertas que encorajam o estudante a pensar profundamente.
Exemplos:
- "O que você observa sobre esta equação?"
- "O que essa parte significa para você?"
- "Como você poderia abordar isso?"

NÃO dê respostas diretas ou passos explícitos ainda.
"""

        elif level == HintLevel.SPECIFIC:
            return f"""
Você está na fase "{phase_name}". O estudante precisa de orientação mais específica.
Faça perguntas direcionadas que estreitam a abordagem:
Exemplos:
- "O que aconteceria se você fizesse [operação específica]?"
- "Qual operação ajudaria a isolar a variável?"
- "Você já considerou usar [técnica específica]?"

Forneça mais contexto, mas ainda não dê a resposta direta.
"""

        elif level == HintLevel.DIRECTIVE:
            return f"""
Você está na fase "{phase_name}". O estudante está com dificuldade e precisa de orientação muito explícita.
Forneça dicas diretivas passo a passo:
Exemplos:
- "Tente subtrair 5 de ambos os lados. O que você obtém?"
- "Divida ambos os lados por 2. Você consegue fazer isso?"
- "Vamos começar isolando x de um lado."

Seja muito explícito sobre O QUE fazer, mas ainda deixe eles FAZEREM o cálculo.
"""

        return ""

    @staticmethod
    def get_encouragement(level: HintLevel) -> str:
        """Get appropriate encouragement based on hint level"""
        if level == HintLevel.GENTLE:
            return "Você está no caminho certo! Continue pensando nisso."
        elif level == HintLevel.SPECIFIC:
            return "Deixe-me te dar um pouco mais de direção para te ajudar."
        elif level == HintLevel.DIRECTIVE:
            return "Sem problemas! Vou te guiar passo a passo."
