"""
Adaptive Learning Engine

Motor adaptativo que orquestra o sistema de aprendizagem personalizada.
Combina grafo de conhecimento, rastreamento de domínio e análise de erros
para criar uma experiência de aprendizado adaptativa.
"""

import json
from typing import Dict, List, Optional, Set
from knowledge_graph_manager import KnowledgeGraphManager
from mastery_tracker import MasteryTracker
from error_analyzer import ErrorAnalyzer, ErrorType
from question_bank import LinearEquationGenerator, Difficulty


class AdaptiveEngine:
    """Motor de aprendizagem adaptativa"""

    def __init__(
        self,
        student_id: str,
        graph_file: str = "knowledge_graph.json",
        progress_file: str = "student_progress.json",
        api_key: Optional[str] = None
    ):
        """
        Initialize adaptive learning engine

        Args:
            student_id: Student identifier
            graph_file: Path to knowledge graph JSON
            progress_file: Path to progress JSON
            api_key: Google Gemini API key for error analysis
        """
        self.student_id = student_id
        self.kg = KnowledgeGraphManager(graph_file)
        self.tracker = MasteryTracker(student_id, progress_file)
        self.analyzer = ErrorAnalyzer(self.kg, api_key)
        self.generator = LinearEquationGenerator()

        # Current session state
        self.current_topic = None
        self.current_difficulty = Difficulty.MEDIUM
        self.error_history = []

    def start_new_session(self, learning_path: str = None) -> Dict:
        """
        Start a new learning session

        Args:
            learning_path: Optional learning path (beginner, intermediate, advanced)

        Returns:
            Session start information
        """
        # Check if diagnostic is needed
        if not self.tracker.is_diagnostic_completed():
            return {
                "status": "diagnostic_required",
                "message": "Complete o teste diagnóstico primeiro",
                "action": "start_diagnostic"
            }

        # Set learning path if provided
        if learning_path:
            self.tracker.set_learning_path(learning_path)

        # Get next recommended topic
        mastered = self.tracker.get_mastered_topics()
        next_topics = self.kg.get_next_topics(mastered)

        if not next_topics:
            return {
                "status": "completed",
                "message": "Parabéns! Você dominou todos os tópicos disponíveis!",
                "mastered_topics": list(mastered)
            }

        # Start with first available topic
        self.current_topic = next_topics[0]
        topic_data = self.kg.get_topic(self.current_topic)

        # Set initial difficulty based on topic
        self.current_difficulty = self._get_initial_difficulty(self.current_topic)

        return {
            "status": "ready",
            "current_topic": self.current_topic,
            "topic_name": topic_data["name"],
            "topic_description": topic_data["description"],
            "difficulty": self.current_difficulty.value,
            "message": f"Vamos começar com: {topic_data['name']}"
        }

    def get_next_question(self) -> Dict:
        """
        Generate the next question based on current state

        Returns:
            Question dictionary with adaptive context
        """
        if not self.current_topic:
            return {
                "error": "Nenhum tópico ativo. Inicie uma sessão primeiro."
            }

        # Map topic to question type
        question_type = self._map_topic_to_question_type(self.current_topic)

        # Generate question
        question = self.generator.generate_question(
            difficulty=self.current_difficulty,
            question_type=question_type
        )

        # Add adaptive context
        question["topic_id"] = self.current_topic
        question["adaptive_context"] = {
            "current_difficulty": self.current_difficulty.value,
            "mastered_topics": list(self.tracker.get_mastered_topics()),
            "session_question_number": self.tracker.get_topic_progress(self.current_topic)["total_questions"] + 1
        }

        return question

    def submit_answer(
        self,
        question_id: str,
        question: str,
        student_answer: str,
        correct_answer: str,
        solution_steps: List[str],
        concepts_tested: List[str]
    ) -> Dict:
        """
        Process student's answer and adapt learning path

        Args:
            question_id: Question identifier
            question: Question text
            student_answer: Student's answer
            correct_answer: Correct answer
            solution_steps: Solution steps
            concepts_tested: Concepts covered in question

        Returns:
            Feedback and next action
        """
        is_correct = str(student_answer).strip() == str(correct_answer).strip()

        # Track the attempt
        self.tracker.track_attempt(
            topic_id=self.current_topic,
            question_id=question_id,
            is_correct=is_correct,
            concepts_tested=concepts_tested,
            error_concepts=[] if is_correct else concepts_tested
        )

        # If incorrect, analyze the error
        if not is_correct:
            error_analysis = self.analyzer.analyze_error(
                topic_id=self.current_topic,
                question=question,
                student_answer=student_answer,
                correct_answer=correct_answer,
                solution_steps=solution_steps
            )

            self.error_history.append(error_analysis)

            # Determine next action based on error
            next_action = self.analyzer.get_next_action(
                topic_id=self.current_topic,
                error_analysis=error_analysis,
                mastered_topics=self.tracker.get_mastered_topics()
            )

            return self._handle_incorrect_answer(
                error_analysis, next_action, solution_steps
            )

        # Correct answer - check for mastery or progression
        return self._handle_correct_answer(solution_steps)

    def _handle_correct_answer(self, solution_steps: List[str]) -> Dict:
        """Handle correct answer and check for progression"""

        # Check mastery
        mastery_threshold = self.kg.get_mastery_threshold(self.current_topic)
        min_questions = self.kg.get_min_questions(self.current_topic)

        mastery_info = self.tracker.calculate_mastery(
            self.current_topic,
            mastery_threshold,
            min_questions
        )

        if mastery_info["is_mastered"]:
            # Topic mastered! Move to next
            topic_data = self.kg.get_topic(self.current_topic)

            # Get next available topics
            mastered = self.tracker.get_mastered_topics()
            next_topics = self.kg.get_next_topics(mastered)

            if next_topics:
                next_topic = next_topics[0]
                next_data = self.kg.get_topic(next_topic)

                return {
                    "status": "topic_mastered",
                    "is_correct": True,
                    "message": f"🎉 Parabéns! Você dominou: {topic_data['name']}",
                    "mastery_info": mastery_info,
                    "next_topic": next_topic,
                    "next_topic_name": next_data["name"],
                    "solution_steps": solution_steps,
                    "action": "advance_topic"
                }
            else:
                return {
                    "status": "all_mastered",
                    "is_correct": True,
                    "message": "🎊 Incrível! Você completou todos os tópicos disponíveis!",
                    "mastery_info": mastery_info,
                    "solution_steps": solution_steps
                }

        # Not mastered yet, continue with maybe increased difficulty
        if mastery_info["accuracy_rate"] > 0.9 and mastery_info["questions_answered"] >= 3:
            # Student is doing very well, increase difficulty
            if self.current_difficulty != Difficulty.HARD:
                self.current_difficulty = Difficulty(
                    min(Difficulty.HARD.value, self.current_difficulty.value + 1)
                )
                difficulty_msg = " Aumentando a dificuldade!"
            else:
                difficulty_msg = ""
        else:
            difficulty_msg = ""

        return {
            "status": "continue",
            "is_correct": True,
            "message": f"✓ Correto!{difficulty_msg}",
            "mastery_info": mastery_info,
            "solution_steps": solution_steps,
            "action": "continue"
        }

    def _handle_incorrect_answer(
        self,
        error_analysis: Dict,
        next_action: Dict,
        solution_steps: List[str]
    ) -> Dict:
        """Handle incorrect answer with adaptive response"""

        action = next_action["action"]

        if action == "REVIEW_PREREQUISITE":
            # Need to go back to prerequisite
            prereq_topic = next_action["target_topic"]
            prereq_data = self.kg.get_topic(prereq_topic)

            self.current_topic = prereq_topic
            self.current_difficulty = Difficulty.EASY
            self.error_history = []

            return {
                "status": "prerequisite_required",
                "is_correct": False,
                "message": f"Vamos revisar primeiro: {prereq_data['name']}",
                "error_analysis": error_analysis,
                "next_action": next_action,
                "solution_steps": solution_steps,
                "new_topic": prereq_topic,
                "new_topic_name": prereq_data["name"],
                "action": "change_topic"
            }

        elif action == "REDUCE_DIFFICULTY":
            # Reduce difficulty
            if self.current_difficulty != Difficulty.EASY:
                self.current_difficulty = Difficulty.EASY

            return {
                "status": "difficulty_reduced",
                "is_correct": False,
                "message": "Vamos tentar questões mais simples para reforçar os conceitos",
                "error_analysis": error_analysis,
                "next_action": next_action,
                "solution_steps": solution_steps,
                "new_difficulty": self.current_difficulty.value,
                "action": "reduce_difficulty"
            }

        else:
            # Continue with same difficulty
            return {
                "status": "continue",
                "is_correct": False,
                "message": "Não desanime! Vamos tentar outra.",
                "error_analysis": error_analysis,
                "solution_steps": solution_steps,
                "hint": self._generate_hint(error_analysis),
                "action": "continue"
            }

    def _generate_hint(self, error_analysis: Dict) -> str:
        """Generate helpful hint based on error analysis"""

        error_type = error_analysis.get("error_type", "")
        explanation = error_analysis.get("explanation", "")

        if error_type == ErrorType.CONCEPTUAL:
            return f"💡 Dica: {explanation}. Revise o conceito e tente novamente."
        elif error_type == ErrorType.PROCEDURAL:
            return f"💡 Dica: {explanation}. Revise os passos da solução."
        elif error_type == ErrorType.ARITHMETIC:
            return "💡 Dica: Verifique seus cálculos aritméticos novamente."
        else:
            return "💡 Dica: Leia a questão com atenção e tente novamente."

    def advance_to_topic(self, topic_id: str) -> Dict:
        """
        Manually advance to a specific topic

        Args:
            topic_id: Topic to advance to

        Returns:
            Topic change confirmation
        """
        # Check if prerequisites are met
        mastered = self.tracker.get_mastered_topics()

        if not self.kg.can_start_topic(topic_id, mastered):
            missing = self.kg.find_prerequisite_gap(topic_id, mastered)
            missing_names = [self.kg.get_topic(m)["name"] for m in missing[:3]]

            return {
                "status": "prerequisites_required",
                "message": f"Você precisa dominar os pré-requisitos primeiro",
                "missing_prerequisites": missing,
                "missing_names": missing_names
            }

        # Set new topic
        self.current_topic = topic_id
        topic_data = self.kg.get_topic(topic_id)
        self.current_difficulty = self._get_initial_difficulty(topic_id)
        self.error_history = []

        return {
            "status": "topic_changed",
            "current_topic": topic_id,
            "topic_name": topic_data["name"],
            "topic_description": topic_data["description"],
            "difficulty": self.current_difficulty.value
        }

    def _get_initial_difficulty(self, topic_id: str) -> Difficulty:
        """Determine initial difficulty for a topic"""

        topic_data = self.kg.get_topic(topic_id)
        topic_difficulty = topic_data.get("difficulty", 2)

        # Map topic difficulty to question difficulty
        if topic_difficulty <= 1:
            return Difficulty.EASY
        elif topic_difficulty <= 3:
            return Difficulty.MEDIUM
        else:
            return Difficulty.HARD

    def _map_topic_to_question_type(self, topic_id: str) -> str:
        """Map knowledge graph topic to question type"""

        # Map topics to question types
        topic_to_type = {
            # Basic prerequisites
            "operacoes_basicas": "basic_operations",
            "numeros_inteiros": "integers",
            "fracoes": "basic_operations",  # Using basic ops for now
            "variaveis_expressoes": "variables_expressions",
            "simplificacao_algebrica": "algebraic_simplification",
            "operacoes_inversas": "inverse_operations",
            "manipulacao_equacoes": "one_step",

            # Linear equations
            "equacoes_lineares_uma_etapa": "one_step",
            "equacoes_lineares_duas_etapas": "two_step",
            "equacoes_lineares_variaveis_ambos_lados": "variables_both_sides",
            "equacoes_lineares": "variables_both_sides",  # Most advanced
        }

        return topic_to_type.get(topic_id, "one_step")

    def get_progress_summary(self) -> Dict:
        """
        Get summary of student's progress

        Returns:
            Progress summary dictionary
        """
        mastered = self.tracker.get_mastered_topics()
        all_topics = list(self.kg.topics.keys())

        progress_by_topic = {}
        for topic_id in all_topics:
            topic_data = self.kg.get_topic(topic_id)
            progress = self.tracker.get_topic_progress(topic_id)

            mastery_info = self.tracker.calculate_mastery(
                topic_id,
                topic_data["mastery_threshold"],
                topic_data["min_questions"]
            )

            progress_by_topic[topic_id] = {
                "name": topic_data["name"],
                "is_mastered": topic_id in mastered,
                "questions_answered": progress["total_questions"],
                "accuracy_rate": mastery_info["accuracy_rate"],
                "can_start": self.kg.can_start_topic(topic_id, mastered)
            }

        return {
            "student_id": self.student_id,
            "mastered_count": len(mastered),
            "total_topics": len(all_topics),
            "completion_percentage": len(mastered) / len(all_topics) * 100,
            "current_topic": self.current_topic,
            "learning_path": self.tracker.get_learning_path(),
            "progress_by_topic": progress_by_topic,
            "next_available": self.kg.get_next_topics(mastered)
        }

    def get_recommended_topics(self) -> List[Dict]:
        """
        Get list of recommended topics for student

        Returns:
            List of recommended topics with context
        """
        mastered = self.tracker.get_mastered_topics()
        available = self.kg.get_next_topics(mastered)

        recommendations = []
        for topic_id in available[:5]:  # Top 5 recommendations
            topic_data = self.kg.get_topic(topic_id)

            recommendations.append({
                "topic_id": topic_id,
                "name": topic_data["name"],
                "description": topic_data["description"],
                "difficulty": topic_data["difficulty"],
                "estimated_questions": topic_data["min_questions"],
                "why_recommended": self._get_recommendation_reason(topic_id, mastered)
            })

        return recommendations

    def _get_recommendation_reason(self, topic_id: str, mastered: Set[str]) -> str:
        """Generate reason why topic is recommended"""

        topic_data = self.kg.get_topic(topic_id)
        difficulty = topic_data["difficulty"]

        prereqs = self.kg.get_prerequisites(topic_id)
        all_prereqs_mastered = all(p in mastered for p in prereqs)

        if difficulty == 1:
            return "Tópico fundamental - ótimo ponto de partida"
        elif all_prereqs_mastered and difficulty <= 2:
            return "Você tem todos os pré-requisitos - sequência natural"
        elif all_prereqs_mastered:
            return "Próximo desafio - você está preparado"
        else:
            return "Disponível agora"
