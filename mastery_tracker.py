"""
Mastery Tracker

Rastreia o progresso e domínio do estudante em cada tópico do grafo de conhecimento.
Combina taxa de acerto com análise de erros conceituais para determinar domínio real.
"""

import json
import os
from typing import Dict, List, Set, Optional
from datetime import datetime
from collections import defaultdict


class MasteryTracker:
    """Rastreador de domínio do estudante"""

    def __init__(self, student_id: str, progress_file: str = "student_progress.json"):
        """
        Initialize mastery tracker for a student

        Args:
            student_id: Unique identifier for the student
            progress_file: Path to progress JSON file
        """
        self.student_id = student_id
        self.progress_file = progress_file
        self.progress = self._load_progress()

    def _load_progress(self) -> Dict:
        """Load student progress from file"""
        if not os.path.exists(self.progress_file):
            return {
                "students": {}
            }

        with open(self.progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_progress(self):
        """Save student progress to file"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)

    def _get_student_data(self) -> Dict:
        """Get or create student data structure"""
        if self.student_id not in self.progress["students"]:
            self.progress["students"][self.student_id] = {
                "created_at": datetime.now().isoformat(),
                "topics": {},
                "mastered_topics": [],
                "current_path": None,
                "diagnostic_completed": False
            }
        return self.progress["students"][self.student_id]

    def _get_topic_data(self, topic_id: str) -> Dict:
        """Get or create topic data for student"""
        student = self._get_student_data()

        if topic_id not in student["topics"]:
            student["topics"][topic_id] = {
                "attempts": [],
                "total_questions": 0,
                "correct_answers": 0,
                "concept_errors": defaultdict(int),
                "last_attempt": None,
                "mastery_achieved": False,
                "mastery_date": None
            }

        return student["topics"][topic_id]

    def track_attempt(
        self,
        topic_id: str,
        question_id: str,
        is_correct: bool,
        concepts_tested: List[str],
        error_concepts: List[str] = None
    ):
        """
        Track a question attempt for mastery calculation

        Args:
            topic_id: Topic being practiced
            question_id: Question identifier
            is_correct: Whether answer was correct
            concepts_tested: List of concepts covered in question
            error_concepts: List of concepts where student made errors
        """
        topic_data = self._get_topic_data(topic_id)

        # Record attempt
        attempt = {
            "question_id": question_id,
            "timestamp": datetime.now().isoformat(),
            "is_correct": is_correct,
            "concepts_tested": concepts_tested,
            "error_concepts": error_concepts or []
        }

        topic_data["attempts"].append(attempt)
        topic_data["total_questions"] += 1
        topic_data["last_attempt"] = datetime.now().isoformat()

        if is_correct:
            topic_data["correct_answers"] += 1

        # Track concept errors
        if error_concepts:
            for concept in error_concepts:
                if concept not in topic_data["concept_errors"]:
                    topic_data["concept_errors"][concept] = 0
                topic_data["concept_errors"][concept] += 1

        self._save_progress()

    def calculate_mastery(self, topic_id: str, mastery_threshold: float = 0.80, min_questions: int = 5) -> Dict:
        """
        Calculate mastery level for a topic

        Args:
            topic_id: Topic to evaluate
            mastery_threshold: Required accuracy rate (0.0-1.0)
            min_questions: Minimum questions needed

        Returns:
            Dictionary with mastery information:
                - is_mastered: bool
                - accuracy_rate: float
                - questions_answered: int
                - recent_performance: float (last 5 questions)
                - conceptual_gaps: list of concepts with repeated errors
                - recommendation: str
        """
        topic_data = self._get_topic_data(topic_id)

        total = topic_data["total_questions"]
        correct = topic_data["correct_answers"]

        # Calculate overall accuracy
        accuracy_rate = correct / total if total > 0 else 0.0

        # Calculate recent performance (last 5 attempts)
        recent_attempts = topic_data["attempts"][-5:] if topic_data["attempts"] else []
        recent_correct = sum(1 for a in recent_attempts if a["is_correct"])
        recent_performance = recent_correct / len(recent_attempts) if recent_attempts else 0.0

        # Identify conceptual gaps (errors in same concept 2+ times)
        conceptual_gaps = [
            concept for concept, count in topic_data["concept_errors"].items()
            if count >= 2
        ]

        # Determine mastery
        has_min_questions = total >= min_questions
        meets_threshold = accuracy_rate >= mastery_threshold
        no_recent_gaps = len([c for c in conceptual_gaps if self._is_recent_error(topic_data, c)]) == 0
        strong_recent = recent_performance >= mastery_threshold

        is_mastered = has_min_questions and meets_threshold and no_recent_gaps and strong_recent

        # Generate recommendation
        if is_mastered:
            recommendation = "Tópico dominado! Pronto para avançar."
        elif not has_min_questions:
            recommendation = f"Continue praticando. Precisa de pelo menos {min_questions} questões."
        elif conceptual_gaps:
            recommendation = f"Revise os conceitos: {', '.join(conceptual_gaps[:3])}"
        elif accuracy_rate < mastery_threshold:
            recommendation = f"Continue praticando para melhorar a precisão (atual: {accuracy_rate:.1%})"
        elif not strong_recent:
            recommendation = "Desempenho recente baixo. Continue praticando para consolidar."
        else:
            recommendation = "Continue praticando para consolidar o domínio."

        return {
            "is_mastered": is_mastered,
            "accuracy_rate": accuracy_rate,
            "questions_answered": total,
            "recent_performance": recent_performance,
            "conceptual_gaps": conceptual_gaps,
            "recommendation": recommendation,
            "needs_more_practice": not has_min_questions or not strong_recent
        }

    def _is_recent_error(self, topic_data: Dict, concept: str, lookback: int = 3) -> bool:
        """Check if concept error occurred in recent attempts"""
        recent_attempts = topic_data["attempts"][-lookback:]

        for attempt in recent_attempts:
            if concept in attempt.get("error_concepts", []):
                return True

        return False

    def is_topic_mastered(self, topic_id: str, mastery_threshold: float = 0.80, min_questions: int = 5) -> bool:
        """
        Check if student has mastered a topic

        Args:
            topic_id: Topic to check
            mastery_threshold: Required accuracy threshold
            min_questions: Minimum questions needed

        Returns:
            True if topic is mastered
        """
        mastery_info = self.calculate_mastery(topic_id, mastery_threshold, min_questions)

        # Update mastery status if achieved
        if mastery_info["is_mastered"]:
            self.mark_topic_mastered(topic_id)

        return mastery_info["is_mastered"]

    def mark_topic_mastered(self, topic_id: str):
        """Mark a topic as mastered"""
        student = self._get_student_data()
        topic_data = self._get_topic_data(topic_id)

        if not topic_data["mastery_achieved"]:
            topic_data["mastery_achieved"] = True
            topic_data["mastery_date"] = datetime.now().isoformat()

            if topic_id not in student["mastered_topics"]:
                student["mastered_topics"].append(topic_id)

            self._save_progress()

    def get_mastered_topics(self) -> Set[str]:
        """Get set of mastered topic IDs"""
        student = self._get_student_data()
        return set(student.get("mastered_topics", []))

    def get_topic_progress(self, topic_id: str) -> Dict:
        """
        Get detailed progress for a topic

        Args:
            topic_id: Topic identifier

        Returns:
            Topic progress data
        """
        return self._get_topic_data(topic_id)

    def get_all_progress(self) -> Dict:
        """Get all progress for the student"""
        return self._get_student_data()

    def set_diagnostic_completed(self, completed: bool = True):
        """Mark diagnostic test as completed"""
        student = self._get_student_data()
        student["diagnostic_completed"] = completed
        self._save_progress()

    def is_diagnostic_completed(self) -> bool:
        """Check if student completed diagnostic"""
        student = self._get_student_data()
        return student.get("diagnostic_completed", False)

    def set_learning_path(self, path_name: str):
        """Set student's learning path"""
        student = self._get_student_data()
        student["current_path"] = path_name
        self._save_progress()

    def get_learning_path(self) -> Optional[str]:
        """Get student's current learning path"""
        student = self._get_student_data()
        return student.get("current_path")

    def get_weak_concepts(self, topic_id: str, threshold: int = 2) -> List[str]:
        """
        Get concepts where student struggles

        Args:
            topic_id: Topic to analyze
            threshold: Minimum errors to be considered weak

        Returns:
            List of weak concept IDs
        """
        topic_data = self._get_topic_data(topic_id)

        weak_concepts = [
            concept for concept, count in topic_data["concept_errors"].items()
            if count >= threshold
        ]

        return weak_concepts

    def get_study_time(self, topic_id: str) -> Dict:
        """
        Calculate time spent on topic

        Args:
            topic_id: Topic identifier

        Returns:
            Dictionary with time statistics
        """
        topic_data = self._get_topic_data(topic_id)
        attempts = topic_data["attempts"]

        if not attempts:
            return {
                "total_attempts": 0,
                "first_attempt": None,
                "last_attempt": None,
                "days_studying": 0
            }

        first = datetime.fromisoformat(attempts[0]["timestamp"])
        last = datetime.fromisoformat(attempts[-1]["timestamp"])
        days_studying = (last - first).days + 1

        return {
            "total_attempts": len(attempts),
            "first_attempt": first.isoformat(),
            "last_attempt": last.isoformat(),
            "days_studying": days_studying
        }

    def reset_topic(self, topic_id: str):
        """Reset progress for a specific topic"""
        student = self._get_student_data()

        if topic_id in student["topics"]:
            del student["topics"][topic_id]

        if topic_id in student.get("mastered_topics", []):
            student["mastered_topics"].remove(topic_id)

        self._save_progress()
