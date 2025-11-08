"""
Polya's Problem-Solving Method Implementation

Defines the 4 phases of mathematical problem solving:
1. Understanding the Problem
2. Devising a Plan
3. Carrying Out the Plan (Execution)
4. Looking Back (Review)
"""

from enum import Enum
from typing import Dict, List


class PolyaPhase(Enum):
    """Enum representing the four phases of Polya's method"""
    UNDERSTANDING = 1
    PLANNING = 2
    EXECUTION = 3
    REVIEW = 4


class PhaseConfig:
    """Configuration for each Polya phase with Socratic question templates"""

    PHASES = {
        PolyaPhase.UNDERSTANDING: {
            "name": "Understanding the Problem",
            "description": "Help the student understand what the problem is asking",
            "goals": [
                "Identify what is being asked for",
                "Identify what information is given",
                "Understand the problem constraints",
                "Restate the problem in own words"
            ],
            "socratic_starters": [
                "What is this problem asking you to find?",
                "What information does the problem give you?",
                "Can you explain in your own words what we need to do?",
                "What does the equation mean?",
                "What are we trying to solve for?"
            ],
            "completion_indicators": [
                "identified unknown variable",
                "stated what to find",
                "restated problem",
                "identified given information"
            ]
        },
        PolyaPhase.PLANNING: {
            "name": "Devising a Plan",
            "description": "Help the student develop a strategy to solve the problem",
            "goals": [
                "Choose an appropriate solving strategy",
                "Identify the mathematical operations needed",
                "Determine the sequence of steps",
                "Consider similar problems solved before"
            ],
            "socratic_starters": [
                "What strategy could you use to solve this?",
                "What mathematical operation might help here?",
                "Have you solved a similar problem before?",
                "What would be your first step?",
                "How can we isolate the variable?"
            ],
            "completion_indicators": [
                "identified strategy",
                "named operations needed",
                "described first step",
                "have a plan"
            ]
        },
        PolyaPhase.EXECUTION: {
            "name": "Carrying Out the Plan",
            "description": "Guide the student through executing their plan step by step",
            "goals": [
                "Execute each step carefully",
                "Show all work clearly",
                "Check each step as you go",
                "Adjust plan if needed"
            ],
            "socratic_starters": [
                "What do you get when you do that operation?",
                "Can you show me the next step?",
                "What happens when you [operation]?",
                "Does that look right to you?",
                "What should we do next?"
            ],
            "completion_indicators": [
                "found solution",
                "calculated answer",
                "solved for variable",
                "got final answer"
            ]
        },
        PolyaPhase.REVIEW: {
            "name": "Looking Back",
            "description": "Help the student verify and reflect on their solution",
            "goals": [
                "Check if the answer makes sense",
                "Verify the solution by substituting back",
                "Reflect on the problem-solving process",
                "Consider alternative methods"
            ],
            "socratic_starters": [
                "Does your answer make sense?",
                "How can you check if your answer is correct?",
                "What happens if you substitute your answer back into the original equation?",
                "Did you answer the original question?",
                "Could you have solved this a different way?"
            ],
            "completion_indicators": [
                "verified answer",
                "checked solution",
                "substituted back",
                "confirmed correct"
            ]
        }
    }

    @staticmethod
    def get_phase_config(phase: PolyaPhase) -> Dict:
        """Get configuration for a specific phase"""
        return PhaseConfig.PHASES[phase]

    @staticmethod
    def get_phase_name(phase: PolyaPhase) -> str:
        """Get the name of a phase"""
        return PhaseConfig.PHASES[phase]["name"]

    @staticmethod
    def get_socratic_starters(phase: PolyaPhase) -> List[str]:
        """Get Socratic question starters for a phase"""
        return PhaseConfig.PHASES[phase]["socratic_starters"]

    @staticmethod
    def get_goals(phase: PolyaPhase) -> List[str]:
        """Get learning goals for a phase"""
        return PhaseConfig.PHASES[phase]["goals"]


class PhaseTransition:
    """Logic for transitioning between Polya phases"""

    @staticmethod
    def should_advance_phase(current_phase: PolyaPhase, conversation_history: List[Dict], student_response: str) -> bool:
        """
        Determine if we should advance to the next phase based on conversation

        Args:
            current_phase: The current Polya phase
            conversation_history: List of previous exchanges
            student_response: The latest student response

        Returns:
            True if should advance to next phase, False otherwise
        """
        if not conversation_history:
            return False

        # Check if student's response indicates phase completion
        phase_config = PhaseConfig.get_phase_config(current_phase)
        completion_indicators = phase_config["completion_indicators"]

        # Simple keyword matching for phase completion
        response_lower = student_response.lower()
        indicators_met = sum(1 for indicator in completion_indicators
                            if any(word in response_lower for word in indicator.split()))

        # Advance if at least 1 completion indicator is met
        # (This is a simple heuristic; can be made more sophisticated)
        if indicators_met >= 1:
            return True

        # Also check if we've had enough exchanges in this phase (fallback)
        exchanges_in_phase = len([msg for msg in conversation_history
                                 if msg.get('phase') == current_phase.name])

        # Different phases have different minimum exchanges
        min_exchanges = {
            PolyaPhase.UNDERSTANDING: 2,
            PolyaPhase.PLANNING: 2,
            PolyaPhase.EXECUTION: 3,
            PolyaPhase.REVIEW: 1
        }

        return exchanges_in_phase >= min_exchanges.get(current_phase, 2)

    @staticmethod
    def get_next_phase(current_phase: PolyaPhase) -> PolyaPhase:
        """Get the next phase in sequence"""
        phase_order = [
            PolyaPhase.UNDERSTANDING,
            PolyaPhase.PLANNING,
            PolyaPhase.EXECUTION,
            PolyaPhase.REVIEW
        ]

        current_index = phase_order.index(current_phase)
        if current_index < len(phase_order) - 1:
            return phase_order[current_index + 1]
        else:
            return current_phase  # Stay in REVIEW phase

    @staticmethod
    def is_complete(current_phase: PolyaPhase) -> bool:
        """Check if we've completed all phases"""
        return current_phase == PolyaPhase.REVIEW
