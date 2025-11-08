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
            "name": "Compreendendo o Problema",
            "description": "Ajudar o estudante a entender o que o problema está pedindo",
            "goals": [
                "Identificar o que está sendo pedido",
                "Identificar quais informações são dadas",
                "Entender as restrições do problema",
                "Reformular o problema com suas próprias palavras"
            ],
            "socratic_starters": [
                "O que este problema está pedindo para você encontrar?",
                "Quais informações o problema te dá?",
                "Você pode explicar com suas próprias palavras o que precisamos fazer?",
                "O que significa esta equação?",
                "O que estamos tentando resolver?"
            ],
            "completion_indicators": [
                "identificou a variável desconhecida",
                "disse o que encontrar",
                "reformulou o problema",
                "identificou as informações dadas"
            ]
        },
        PolyaPhase.PLANNING: {
            "name": "Planejando a Solução",
            "description": "Ajudar o estudante a desenvolver uma estratégia para resolver o problema",
            "goals": [
                "Escolher uma estratégia de resolução apropriada",
                "Identificar as operações matemáticas necessárias",
                "Determinar a sequência de passos",
                "Considerar problemas similares resolvidos anteriormente"
            ],
            "socratic_starters": [
                "Que estratégia você poderia usar para resolver isso?",
                "Que operação matemática pode ajudar aqui?",
                "Você já resolveu um problema parecido antes?",
                "Qual seria seu primeiro passo?",
                "Como podemos isolar a variável?"
            ],
            "completion_indicators": [
                "identificou uma estratégia",
                "nomeou as operações necessárias",
                "descreveu o primeiro passo",
                "tem um plano"
            ]
        },
        PolyaPhase.EXECUTION: {
            "name": "Executando o Plano",
            "description": "Guiar o estudante através da execução do plano passo a passo",
            "goals": [
                "Executar cada passo com cuidado",
                "Mostrar todo o trabalho claramente",
                "Verificar cada passo conforme avança",
                "Ajustar o plano se necessário"
            ],
            "socratic_starters": [
                "O que você obtém quando faz essa operação?",
                "Pode me mostrar o próximo passo?",
                "O que acontece quando você faz isso?",
                "Isso parece certo para você?",
                "O que devemos fazer a seguir?"
            ],
            "completion_indicators": [
                "encontrou a solução",
                "calculou a resposta",
                "resolveu para a variável",
                "obteve a resposta final"
            ]
        },
        PolyaPhase.REVIEW: {
            "name": "Revisando a Solução",
            "description": "Ajudar o estudante a verificar e refletir sobre sua solução",
            "goals": [
                "Verificar se a resposta faz sentido",
                "Verificar a solução substituindo de volta",
                "Refletir sobre o processo de resolução",
                "Considerar métodos alternativos"
            ],
            "socratic_starters": [
                "Sua resposta faz sentido?",
                "Como você pode verificar se sua resposta está correta?",
                "O que acontece se você substituir sua resposta de volta na equação original?",
                "Você respondeu a pergunta original?",
                "Você poderia ter resolvido isso de outra forma?"
            ],
            "completion_indicators": [
                "verificou a resposta",
                "checou a solução",
                "substituiu de volta",
                "confirmou que está correto"
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
