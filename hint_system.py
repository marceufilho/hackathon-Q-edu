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
        "i don't know",
        "i'm not sure",
        "i'm stuck",
        "i don't understand",
        "i'm confused",
        "no idea",
        "can you help",
        "i give up",
        "help me",
        "what do i do",
        "i can't",
        "don't know how"
    ]

    VAGUE_RESPONSES = [
        "idk",
        "umm",
        "uh",
        "hmm",
        "maybe",
        "i think",
        "not sure"
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
You are in the "{phase_name}" phase. Ask open-ended Socratic questions that encourage the student to think deeply.
Examples:
- "What do you notice about this equation?"
- "What does this part mean to you?"
- "How might you approach this?"

Do NOT give direct answers or explicit steps yet.
"""

        elif level == HintLevel.SPECIFIC:
            return f"""
You are in the "{phase_name}" phase. The student needs more specific guidance.
Ask pointed questions that narrow down the approach:
Examples:
- "What would happen if you [specific operation]?"
- "Which operation would help isolate the variable?"
- "Have you considered using [specific technique]?"

Provide more context, but still don't give the direct answer.
"""

        elif level == HintLevel.DIRECTIVE:
            return f"""
You are in the "{phase_name}" phase. The student is struggling and needs very explicit guidance.
Provide step-by-step directive hints:
Examples:
- "Try subtracting 5 from both sides. What do you get?"
- "Divide both sides by 2. Can you do that?"
- "Let's start by isolating x on one side."

Be very explicit about WHAT to do, but still let them DO the calculation.
"""

        return ""

    @staticmethod
    def get_encouragement(level: HintLevel) -> str:
        """Get appropriate encouragement based on hint level"""
        if level == HintLevel.GENTLE:
            return "You're on the right track! Keep thinking about it."
        elif level == HintLevel.SPECIFIC:
            return "Let me give you a bit more direction to help you out."
        elif level == HintLevel.DIRECTIVE:
            return "No worries! Let me guide you step by step."
