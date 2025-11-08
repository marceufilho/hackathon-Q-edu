"""
Error Analyzer

Analisa erros dos estudantes para identificar lacunas conceituais e determinar
se precisam voltar para tópicos pré-requisitos ou apenas reduzir dificuldade.
"""

import os
import google.generativeai as genai
from typing import Dict, List, Optional, Set
from knowledge_graph_manager import KnowledgeGraphManager


class ErrorType:
    """Types of errors students can make"""
    CONCEPTUAL = "conceptual"  # Fundamental misunderstanding
    PROCEDURAL = "procedural"  # Wrong steps but concept understood
    ARITHMETIC = "arithmetic"  # Simple calculation error
    CARELESS = "careless"      # Silly mistake, knows the concept


class ErrorAnalyzer:
    """Analisa erros dos estudantes para identificar padrões e lacunas"""

    def __init__(self, knowledge_graph: KnowledgeGraphManager, api_key: Optional[str] = None):
        """
        Initialize error analyzer

        Args:
            knowledge_graph: Knowledge graph manager instance
            api_key: Google Gemini API key
        """
        self.kg = knowledge_graph
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
        else:
            self.model = None

    def analyze_error(
        self,
        topic_id: str,
        question: str,
        student_answer: str,
        correct_answer: str,
        solution_steps: List[str]
    ) -> Dict:
        """
        Analyze a student's error to identify the type and affected concepts

        Args:
            topic_id: Topic being practiced
            question: The question text
            student_answer: Student's incorrect answer
            correct_answer: The correct answer
            solution_steps: Steps to solve the problem

        Returns:
            Dictionary with error analysis:
                - error_type: Type of error
                - affected_concepts: List of concepts where error occurred
                - prerequisite_gaps: Prerequisites that might be missing
                - recommendation: What to do next
                - explanation: Detailed analysis
        """
        # Get topic concepts
        topic_concepts = self.kg.get_topic_concepts(topic_id)

        # Use LLM for sophisticated error analysis if available
        if self.model:
            return self._llm_analyze_error(
                topic_id, question, student_answer, correct_answer,
                solution_steps, topic_concepts
            )
        else:
            # Fallback to heuristic analysis
            return self._heuristic_analyze_error(
                topic_id, question, student_answer, correct_answer,
                solution_steps, topic_concepts
            )

    def _llm_analyze_error(
        self,
        topic_id: str,
        question: str,
        student_answer: str,
        correct_answer: str,
        solution_steps: List[str],
        topic_concepts: List[str]
    ) -> Dict:
        """Use LLM to analyze error in depth"""

        topic = self.kg.get_topic(topic_id)
        topic_name = topic["name"] if topic else topic_id

        prompt = f"""Analise o erro cometido por um estudante em uma questão de matemática.

TÓPICO: {topic_name}
CONCEITOS COBERTOS: {', '.join(topic_concepts)}

QUESTÃO:
{question}

RESPOSTA DO ESTUDANTE: {student_answer}
RESPOSTA CORRETA: {correct_answer}

PASSOS DA SOLUÇÃO:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(solution_steps))}

Analise o erro e retorne uma classificação estruturada:

1. TIPO DE ERRO (escolha um):
   - CONCEPTUAL: Erro fundamental no entendimento do conceito
   - PROCEDURAL: Entende o conceito mas aplicou passos errados
   - ARITHMETIC: Erro de cálculo aritmético simples
   - CARELESS: Erro bobo, distração (estudante sabe o conceito)

2. CONCEITOS AFETADOS: Quais conceitos específicos foram mal aplicados?
   (use os conceitos da lista: {', '.join(topic_concepts)})

3. INDICA LACUNA EM PRÉ-REQUISITO: Este erro indica que o estudante não dominou
   algum tópico pré-requisito? Se sim, qual?

4. RECOMENDAÇÃO: O que fazer?
   - VOLTAR_PREREQUISITO: Precisa revisar um pré-requisito
   - REDUZIR_DIFICULDADE: Continuar no tópico mas com questões mais fáceis
   - CONTINUAR: Erro isolado, pode continuar normalmente
   - REFORCAR: Precisa mais prática no mesmo nível

Formate a resposta EXATAMENTE assim:
TIPO: [tipo]
CONCEITOS: [conceito1, conceito2, ...]
PREREQUISITO_FALTANTE: [id do tópico ou NENHUM]
RECOMENDACAO: [recomendação]
EXPLICACAO: [explicação breve em 1-2 frases]
"""

        try:
            response = self.model.generate_content(prompt)
            return self._parse_llm_response(response.text, topic_id)
        except Exception as e:
            print(f"Erro na análise LLM: {e}")
            return self._heuristic_analyze_error(
                topic_id, question, student_answer, correct_answer,
                solution_steps, topic_concepts
            )

    def _parse_llm_response(self, response_text: str, topic_id: str) -> Dict:
        """Parse structured LLM response"""

        lines = response_text.strip().split('\n')
        result = {
            "error_type": ErrorType.CONCEPTUAL,
            "affected_concepts": [],
            "prerequisite_gaps": [],
            "recommendation": "CONTINUAR",
            "explanation": "Análise não disponível"
        }

        for line in lines:
            line = line.strip()
            if line.startswith("TIPO:"):
                error_type = line.split(":", 1)[1].strip().lower()
                result["error_type"] = error_type

            elif line.startswith("CONCEITOS:"):
                concepts_str = line.split(":", 1)[1].strip()
                concepts = [c.strip() for c in concepts_str.split(",") if c.strip()]
                result["affected_concepts"] = concepts

            elif line.startswith("PREREQUISITO_FALTANTE:"):
                prereq = line.split(":", 1)[1].strip()
                if prereq and prereq.upper() != "NENHUM":
                    result["prerequisite_gaps"] = [prereq]

            elif line.startswith("RECOMENDACAO:"):
                result["recommendation"] = line.split(":", 1)[1].strip()

            elif line.startswith("EXPLICACAO:"):
                result["explanation"] = line.split(":", 1)[1].strip()

        return result

    def _heuristic_analyze_error(
        self,
        topic_id: str,
        question: str,
        student_answer: str,
        correct_answer: str,
        solution_steps: List[str],
        topic_concepts: List[str]
    ) -> Dict:
        """Simple heuristic-based error analysis"""

        # Very basic analysis - in production, LLM is much better
        student_lower = str(student_answer).lower()

        # Check if it's close to correct (likely arithmetic error)
        try:
            student_num = float(student_answer)
            correct_num = float(correct_answer)

            # If within 10% or off by small integer, likely arithmetic
            if abs(student_num - correct_num) <= max(abs(correct_num) * 0.1, 2):
                return {
                    "error_type": ErrorType.ARITHMETIC,
                    "affected_concepts": [],
                    "prerequisite_gaps": [],
                    "recommendation": "CONTINUAR",
                    "explanation": "Erro aritmético pequeno, provavelmente distração"
                }
        except (ValueError, TypeError):
            pass

        # Check for confusion indicators
        confusion_words = ["não sei", "?", "talvez", "acho"]
        if any(word in student_lower for word in confusion_words):
            return {
                "error_type": ErrorType.CONCEPTUAL,
                "affected_concepts": topic_concepts[:1],  # Flag first concept
                "prerequisite_gaps": self.kg.get_prerequisites(topic_id),
                "recommendation": "VOLTAR_PREREQUISITO",
                "explanation": "Resposta indica confusão conceitual"
            }

        # Default: procedural error
        return {
            "error_type": ErrorType.PROCEDURAL,
            "affected_concepts": topic_concepts[:1],
            "prerequisite_gaps": [],
            "recommendation": "REFORCAR",
            "explanation": "Erro no procedimento de resolução"
        }

    def identify_prerequisite_gaps(
        self,
        topic_id: str,
        error_history: List[Dict],
        mastered_topics: Set[str]
    ) -> List[str]:
        """
        Identify which prerequisites are likely missing based on error patterns

        Args:
            topic_id: Current topic
            error_history: List of error analysis results
            mastered_topics: Topics student has mastered

        Returns:
            List of prerequisite topic IDs that need review
        """
        if not error_history:
            return []

        # Collect all prerequisite gaps mentioned in errors
        gap_candidates = set()

        for error in error_history:
            for prereq in error.get("prerequisite_gaps", []):
                gap_candidates.add(prereq)

        # Filter to only include actual prerequisites
        all_prereqs = self.kg.get_all_prerequisites(topic_id)
        actual_gaps = [
            prereq for prereq in gap_candidates
            if prereq in all_prereqs and prereq not in mastered_topics
        ]

        # Sort by difficulty (easier first for remediation)
        actual_gaps.sort(key=lambda t: self.kg.get_topic(t).get("difficulty", 99))

        return actual_gaps

    def should_reduce_difficulty(self, error_history: List[Dict], lookback: int = 3) -> bool:
        """
        Determine if difficulty should be reduced (vs going back to prerequisites)

        Args:
            error_history: Recent error analyses
            lookback: Number of recent errors to consider

        Returns:
            True if should reduce difficulty, False if should go to prerequisites
        """
        if not error_history:
            return False

        recent_errors = error_history[-lookback:]

        # Count error types
        conceptual_count = sum(
            1 for e in recent_errors
            if e.get("error_type") == ErrorType.CONCEPTUAL
        )

        procedural_count = sum(
            1 for e in recent_errors
            if e.get("error_type") == ErrorType.PROCEDURAL
        )

        # If mostly procedural/arithmetic, reduce difficulty
        # If mostly conceptual, go back to prerequisites
        return procedural_count > conceptual_count

    def get_next_action(
        self,
        topic_id: str,
        error_analysis: Dict,
        mastered_topics: Set[str]
    ) -> Dict:
        """
        Determine the next action based on error analysis

        Args:
            topic_id: Current topic
            error_analysis: Analysis of the error
            mastered_topics: Topics student has mastered

        Returns:
            Dictionary with:
                - action: CONTINUE, REDUCE_DIFFICULTY, REVIEW_PREREQUISITE
                - target_topic: Topic to work on (if changing)
                - difficulty_adjustment: Difficulty change (-1, 0, +1)
                - explanation: Why this action
        """
        recommendation = error_analysis.get("recommendation", "CONTINUAR")
        error_type = error_analysis.get("error_type", ErrorType.CONCEPTUAL)

        if recommendation == "VOLTAR_PREREQUISITO":
            # Find which prerequisite to review
            prereq_gaps = error_analysis.get("prerequisite_gaps", [])

            if prereq_gaps:
                # Pick the first unmastered prerequisite
                target = None
                for prereq in prereq_gaps:
                    if prereq not in mastered_topics:
                        target = prereq
                        break

                if target:
                    return {
                        "action": "REVIEW_PREREQUISITE",
                        "target_topic": target,
                        "difficulty_adjustment": 0,
                        "explanation": f"Erro indica lacuna em: {self.kg.get_topic(target)['name']}"
                    }

        if recommendation == "REDUZIR_DIFICULDADE":
            return {
                "action": "REDUCE_DIFFICULTY",
                "target_topic": topic_id,
                "difficulty_adjustment": -1,
                "explanation": "Reduzindo dificuldade para reforçar conceitos"
            }

        if recommendation == "REFORCAR":
            return {
                "action": "CONTINUE",
                "target_topic": topic_id,
                "difficulty_adjustment": 0,
                "explanation": "Continue praticando no mesmo nível"
            }

        # Default: continue
        return {
            "action": "CONTINUE",
            "target_topic": topic_id,
            "difficulty_adjustment": 0,
            "explanation": "Continue avançando normalmente"
        }

    def get_error_patterns(self, error_history: List[Dict]) -> Dict:
        """
        Analyze patterns in error history

        Args:
            error_history: List of error analyses

        Returns:
            Dictionary with pattern analysis
        """
        if not error_history:
            return {
                "total_errors": 0,
                "error_type_distribution": {},
                "most_affected_concepts": [],
                "trending": "neutral"
            }

        # Count error types
        type_counts = {}
        for error in error_history:
            error_type = error.get("error_type", "unknown")
            type_counts[error_type] = type_counts.get(error_type, 0) + 1

        # Count affected concepts
        concept_counts = {}
        for error in error_history:
            for concept in error.get("affected_concepts", []):
                concept_counts[concept] = concept_counts.get(concept, 0) + 1

        # Find most affected concepts
        most_affected = sorted(
            concept_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        # Determine trend (improving or worsening)
        if len(error_history) >= 5:
            recent_conceptual = sum(
                1 for e in error_history[-3:]
                if e.get("error_type") == ErrorType.CONCEPTUAL
            )
            older_conceptual = sum(
                1 for e in error_history[-6:-3]
                if e.get("error_type") == ErrorType.CONCEPTUAL
            )

            if recent_conceptual < older_conceptual:
                trending = "improving"
            elif recent_conceptual > older_conceptual:
                trending = "worsening"
            else:
                trending = "stable"
        else:
            trending = "neutral"

        return {
            "total_errors": len(error_history),
            "error_type_distribution": type_counts,
            "most_affected_concepts": [concept for concept, count in most_affected],
            "trending": trending
        }
