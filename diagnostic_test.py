"""
Diagnostic Test

Teste diagnóstico inicial para determinar o nível do estudante
e identificar tópicos já dominados antes de iniciar o aprendizado.
"""

import uuid
from typing import Dict, List, Set
from knowledge_graph_manager import KnowledgeGraphManager
from mastery_tracker import MasteryTracker
from question_bank import LinearEquationGenerator, Difficulty


class DiagnosticTest:
    """Teste diagnóstico para avaliar nível inicial do estudante"""

    def __init__(
        self,
        student_id: str,
        graph_file: str = "knowledge_graph.json",
        progress_file: str = "student_progress.json"
    ):
        """
        Initialize diagnostic test

        Args:
            student_id: Student identifier
            graph_file: Path to knowledge graph
            progress_file: Path to progress file
        """
        self.student_id = student_id
        self.kg = KnowledgeGraphManager(graph_file)
        self.tracker = MasteryTracker(student_id, progress_file)
        self.generator = LinearEquationGenerator()

        # Test state
        self.test_questions = []
        self.current_question_index = 0
        self.test_started = False

    def generate_diagnostic_test(self, questions_per_topic: int = 3) -> Dict:
        """
        Generate a diagnostic test

        Args:
            questions_per_topic: Number of questions per diagnostic topic

        Returns:
            Test information
        """
        diagnostic_topics = self.kg.get_diagnostic_topics()

        if not diagnostic_topics:
            return {
                "error": "Nenhum tópico diagnóstico configurado"
            }

        self.test_questions = []

        # Generate questions for each diagnostic topic
        for topic_id in diagnostic_topics:
            topic_data = self.kg.get_topic(topic_id)

            if not topic_data:
                continue

            # Map topic to question type
            question_type = self._map_topic_to_question_type(topic_id)

            # Determine difficulty based on topic difficulty
            topic_difficulty = topic_data.get("difficulty", 2)

            if topic_difficulty <= 1:
                difficulty = Difficulty.EASY
            elif topic_difficulty <= 2:
                difficulty = Difficulty.MEDIUM
            else:
                difficulty = Difficulty.HARD

            # Generate questions
            for i in range(questions_per_topic):
                question = self.generator.generate_question(
                    difficulty=difficulty,
                    question_type=question_type
                )

                # Add metadata
                question["question_id"] = str(uuid.uuid4())
                question["topic_id"] = topic_id
                question["topic_name"] = topic_data["name"]
                question["is_diagnostic"] = True
                question["concepts"] = self.kg.get_topic_concepts(topic_id)

                self.test_questions.append(question)

        self.test_started = True
        self.current_question_index = 0

        return {
            "status": "test_generated",
            "total_questions": len(self.test_questions),
            "topics_covered": len(diagnostic_topics),
            "diagnostic_topics": [
                {
                    "topic_id": tid,
                    "name": self.kg.get_topic(tid)["name"]
                }
                for tid in diagnostic_topics
            ],
            "message": f"Teste diagnóstico pronto com {len(self.test_questions)} questões"
        }

    def get_next_question(self) -> Dict:
        """
        Get next diagnostic question

        Returns:
            Question or completion message
        """
        if not self.test_started:
            return {
                "error": "Teste não iniciado. Chame generate_diagnostic_test() primeiro."
            }

        if self.current_question_index >= len(self.test_questions):
            return {
                "status": "test_completed",
                "message": "Teste diagnóstico completo!",
                "action": "evaluate_results"
            }

        question = self.test_questions[self.current_question_index]

        return {
            "status": "question",
            "question_number": self.current_question_index + 1,
            "total_questions": len(self.test_questions),
            "question": question,
            "progress_percentage": (self.current_question_index / len(self.test_questions)) * 100
        }

    def submit_answer(self, question_id: str, student_answer: str) -> Dict:
        """
        Submit answer to diagnostic question

        Args:
            question_id: Question identifier
            student_answer: Student's answer

        Returns:
            Feedback and next question
        """
        # Find the question
        question = None
        for q in self.test_questions:
            if q["question_id"] == question_id:
                question = q
                break

        if not question:
            return {
                "error": "Questão não encontrada"
            }

        # Check answer
        is_correct = str(student_answer).strip() == str(question["answer"]).strip()

        # Track the attempt
        self.tracker.track_attempt(
            topic_id=question["topic_id"],
            question_id=question_id,
            is_correct=is_correct,
            concepts_tested=question.get("concepts", []),
            error_concepts=[] if is_correct else question.get("concepts", [])
        )

        # Move to next question
        self.current_question_index += 1

        # Check if test is complete
        if self.current_question_index >= len(self.test_questions):
            # Evaluate and generate results
            results = self.evaluate_results()

            return {
                "status": "test_completed",
                "is_correct": is_correct,
                "correct_answer": question["answer"],
                "solution_steps": question.get("steps", []),
                "diagnostic_results": results
            }

        # Return next question
        next_question = self.get_next_question()

        return {
            "status": "answered",
            "is_correct": is_correct,
            "correct_answer": question["answer"],
            "solution_steps": question.get("steps", []),
            "next_question": next_question
        }

    def evaluate_results(self) -> Dict:
        """
        Evaluate diagnostic test results and recommend learning path

        Returns:
            Evaluation results with recommendations
        """
        diagnostic_topics = self.kg.get_diagnostic_topics()

        # Calculate performance per topic
        topic_performance = {}
        total_correct = 0
        total_questions = 0

        for topic_id in diagnostic_topics:
            topic_data = self.kg.get_topic(topic_id)
            mastery_threshold = topic_data.get("mastery_threshold", 0.75)
            min_questions = 3  # We generated 3 per topic

            mastery_info = self.tracker.calculate_mastery(
                topic_id, mastery_threshold, min_questions
            )

            topic_performance[topic_id] = {
                "name": topic_data["name"],
                "accuracy": mastery_info["accuracy_rate"],
                "is_mastered": mastery_info["is_mastered"],
                "questions_answered": mastery_info["questions_answered"]
            }

            total_correct += int(mastery_info["accuracy_rate"] * mastery_info["questions_answered"])
            total_questions += mastery_info["questions_answered"]

        overall_accuracy = total_correct / total_questions if total_questions > 0 else 0

        # Determine learning path
        learning_path = self._determine_learning_path(topic_performance, overall_accuracy)

        # Mark topics as mastered if they are
        mastered_topics = []
        for topic_id, performance in topic_performance.items():
            if performance["is_mastered"]:
                self.tracker.mark_topic_mastered(topic_id)
                mastered_topics.append(topic_id)

        # Mark diagnostic as complete
        self.tracker.set_diagnostic_completed(True)
        self.tracker.set_learning_path(learning_path["path_name"])

        # Get recommended starting point
        mastered_set = self.tracker.get_mastered_topics()
        next_topics = self.kg.get_next_topics(mastered_set)

        return {
            "overall_accuracy": overall_accuracy,
            "total_questions": total_questions,
            "total_correct": total_correct,
            "topic_performance": topic_performance,
            "mastered_topics": mastered_topics,
            "recommended_path": learning_path,
            "next_topics": [
                {
                    "topic_id": tid,
                    "name": self.kg.get_topic(tid)["name"],
                    "description": self.kg.get_topic(tid)["description"]
                }
                for tid in next_topics[:3]
            ],
            "message": self._generate_feedback_message(learning_path, overall_accuracy)
        }

    def _determine_learning_path(
        self,
        topic_performance: Dict,
        overall_accuracy: float
    ) -> Dict:
        """
        Determine appropriate learning path based on performance

        Args:
            topic_performance: Performance per topic
            overall_accuracy: Overall accuracy rate

        Returns:
            Learning path recommendation
        """
        # Count mastered basic topics
        basic_topics = ["operacoes_basicas", "numeros_inteiros"]
        basic_mastered = sum(
            1 for tid in basic_topics
            if tid in topic_performance and topic_performance[tid]["is_mastered"]
        )

        # Count mastered intermediate topics
        intermediate_topics = ["variaveis_expressoes", "operacoes_inversas", "simplificacao_algebrica"]
        intermediate_mastered = sum(
            1 for tid in intermediate_topics
            if tid in topic_performance and topic_performance[tid]["is_mastered"]
        )

        # Determine path
        if overall_accuracy >= 0.80 and intermediate_mastered >= 2:
            path_name = "advanced"
            description = "Você tem uma base sólida! Vamos direto para equações lineares."
            reason = "Alto desempenho em tópicos intermediários"

        elif overall_accuracy >= 0.60 and basic_mastered >= 1:
            path_name = "intermediate"
            description = "Você conhece o básico! Vamos focar em álgebra."
            reason = "Bom conhecimento de operações básicas"

        else:
            path_name = "beginner"
            description = "Vamos começar do início para construir uma base forte!"
            reason = "Melhor começar pelos fundamentos"

        path_data = self.kg.get_learning_path(path_name)

        return {
            "path_name": path_name,
            "path_title": path_data["name"],
            "description": description,
            "reason": reason,
            "path_topics": path_data["path"],
            "start_topic": path_data["start_topic"]
        }

    def _generate_feedback_message(self, learning_path: Dict, accuracy: float) -> str:
        """Generate encouraging feedback message"""

        if accuracy >= 0.80:
            performance = "Excelente"
        elif accuracy >= 0.60:
            performance = "Bom"
        elif accuracy >= 0.40:
            performance = "Razoável"
        else:
            performance = "Inicial"

        message = f"""{performance} desempenho no teste diagnóstico!

{learning_path['description']}

Motivo: {learning_path['reason']}

Você seguirá o caminho '{learning_path['path_title']}' com {len(learning_path['path_topics'])} tópicos.
"""

        return message

    def _map_topic_to_question_type(self, topic_id: str) -> str:
        """Map diagnostic topic to question type"""

        # Use appropriate question types for each topic
        topic_mapping = {
            "operacoes_basicas": "basic_operations",
            "numeros_inteiros": "integers",
            "fracoes": "basic_operations",
            "variaveis_expressoes": "variables_expressions",
            "simplificacao_algebrica": "algebraic_simplification",
            "operacoes_inversas": "inverse_operations",
            "manipulacao_equacoes": "one_step",
            "equacoes_lineares_uma_etapa": "one_step",
            "equacoes_lineares_duas_etapas": "two_step"
        }

        return topic_mapping.get(topic_id, "one_step")

    def get_test_status(self) -> Dict:
        """
        Get current test status

        Returns:
            Test status information
        """
        return {
            "test_started": self.test_started,
            "total_questions": len(self.test_questions),
            "current_question": self.current_question_index,
            "questions_remaining": len(self.test_questions) - self.current_question_index,
            "is_completed": self.current_question_index >= len(self.test_questions)
        }

    def reset_test(self):
        """Reset diagnostic test for retake"""
        self.test_questions = []
        self.current_question_index = 0
        self.test_started = False

        # Reset diagnostic completion status
        self.tracker.set_diagnostic_completed(False)
