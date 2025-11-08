"""
Question Manager

Manages practice questions with JSON file persistence.
Tracks question metadata, student progress, and attempts.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from question_bank import LinearEquationGenerator, Difficulty


class QuestionManager:
    """Manages practice questions with file-based persistence"""

    def __init__(self, questions_file: str = "questions.json"):
        """
        Initialize the question manager

        Args:
            questions_file: Path to JSON file for storing questions
        """
        self.questions_file = questions_file
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create questions file if it doesn't exist"""
        if not os.path.exists(self.questions_file):
            initial_data = {
                "questions": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "total_questions": 0,
                    "total_attempts": 0,
                    "total_completed": 0
                }
            }
            with open(self.questions_file, 'w') as f:
                json.dump(initial_data, f, indent=2)

    def _load_data(self) -> Dict:
        """Load questions data from file"""
        with open(self.questions_file, 'r') as f:
            return json.load(f)

    def _save_data(self, data: Dict):
        """Save questions data to file"""
        data["metadata"]["updated_at"] = datetime.now().isoformat()
        with open(self.questions_file, 'w') as f:
            json.dump(data, f, indent=2)

    # Topic mapping: maps topic display names to question types
    TOPIC_TO_QUESTION_TYPE = {
        "operações básicas": "basic_operations",
        "números inteiros": "integers",
        "variáveis e expressões": "variables_expressions",
        "simplificação algébrica": "algebraic_simplification",
        "operações inversas": "inverse_operations",
        "equações lineares - uma etapa": "one_step",
        "equações lineares - duas etapas": "two_step",
        "equações com variáveis em ambos os lados": "variables_both_sides",
        "equações lineares": "two_step"  # Default to two_step for general linear equations
    }

    def generate_questions(self, count: int = 10, difficulty: str = None, topic: str = None) -> List[Dict]:
        """
        Generate and store new practice questions

        Args:
            count: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard, or None for mixed)
            topic: Topic to generate questions for (e.g., "Equações Lineares" or "Operações Básicas")

        Returns:
            List of generated questions with IDs
        """
        data = self._load_data()

        # Convert difficulty string to enum
        diff_enum = None
        if difficulty:
            diff_enum = Difficulty(difficulty.lower())

        # Determine question type from topic
        question_type = None
        if topic:
            question_type = self.TOPIC_TO_QUESTION_TYPE.get(topic.lower())
            if question_type is None:
                raise ValueError(
                    f"Unknown or unsupported topic: '{topic}'. "
                    f"Available topics: {', '.join(self.TOPIC_TO_QUESTION_TYPE.keys())}"
                )

        # Generate questions
        generated = []
        for _ in range(count):
            q = LinearEquationGenerator.generate_question(diff_enum, question_type)
            generated.append(q)

        # Add metadata and IDs
        questions_with_metadata = []
        for q in generated:
            question_id = str(uuid.uuid4())
            question_data = {
                "id": question_id,
                "problem": q["problem"],
                "equation": q["equation"],
                "answer": q["answer"],
                "steps": q["steps"],
                "difficulty": q["difficulty"],
                "type": q["type"],
                "topic": q["topic"],
                "created_at": datetime.now().isoformat(),
                "attempts": 0,
                "completed": False,
                "session_ids": []
            }
            questions_with_metadata.append(question_data)
            data["questions"].append(question_data)

        # Update metadata
        data["metadata"]["total_questions"] = len(data["questions"])
        data["metadata"]["last_generated"] = datetime.now().isoformat()

        self._save_data(data)
        return questions_with_metadata

    def get_question(self, question_id: str) -> Optional[Dict]:
        """
        Get a specific question by ID

        Args:
            question_id: The question identifier

        Returns:
            Question data or None if not found
        """
        data = self._load_data()
        for question in data["questions"]:
            if question["id"] == question_id:
                return question
        return None

    def list_questions(
        self,
        difficulty: str = None,
        completed: bool = None,
        limit: int = None,
        topic: str = None
    ) -> List[Dict]:
        """
        List questions with optional filtering

        Args:
            difficulty: Filter by difficulty level
            completed: Filter by completion status
            limit: Maximum number of questions to return
            topic: Filter by topic (e.g., "Equações Lineares" or "Operações Básicas")

        Returns:
            List of questions matching criteria
        """
        data = self._load_data()
        questions = data["questions"]

        # Apply filters
        if difficulty:
            questions = [q for q in questions if q["difficulty"] == difficulty.lower()]

        if completed is not None:
            questions = [q for q in questions if q["completed"] == completed]

        if topic:
            # Case-insensitive topic matching
            questions = [q for q in questions if q.get("topic", "").lower() == topic.lower()]

        # Sort by created_at (newest first)
        questions = sorted(questions, key=lambda x: x["created_at"], reverse=True)

        # Apply limit
        if limit:
            questions = questions[:limit]

        return questions

    def mark_attempted(self, question_id: str, session_id: str) -> bool:
        """
        Mark a question as attempted and link to teaching session

        Args:
            question_id: The question identifier
            session_id: The teaching session ID

        Returns:
            True if successful, False if question not found
        """
        data = self._load_data()

        for question in data["questions"]:
            if question["id"] == question_id:
                question["attempts"] += 1
                if session_id not in question["session_ids"]:
                    question["session_ids"].append(session_id)
                question["last_attempted"] = datetime.now().isoformat()

                # Update global metadata
                data["metadata"]["total_attempts"] = sum(q["attempts"] for q in data["questions"])

                self._save_data(data)
                return True

        return False

    def mark_completed(self, question_id: str) -> bool:
        """
        Mark a question as completed

        Args:
            question_id: The question identifier

        Returns:
            True if successful, False if question not found
        """
        data = self._load_data()

        for question in data["questions"]:
            if question["id"] == question_id:
                if not question["completed"]:
                    question["completed"] = True
                    question["completed_at"] = datetime.now().isoformat()

                    # Update global metadata
                    data["metadata"]["total_completed"] = sum(
                        1 for q in data["questions"] if q["completed"]
                    )

                    self._save_data(data)
                return True

        return False

    def delete_question(self, question_id: str) -> bool:
        """
        Delete a question

        Args:
            question_id: The question identifier

        Returns:
            True if deleted, False if not found
        """
        data = self._load_data()
        initial_count = len(data["questions"])

        data["questions"] = [q for q in data["questions"] if q["id"] != question_id]

        if len(data["questions"]) < initial_count:
            data["metadata"]["total_questions"] = len(data["questions"])
            self._save_data(data)
            return True

        return False

    def get_stats(self) -> Dict:
        """
        Get overall statistics

        Returns:
            Dictionary with question bank statistics
        """
        data = self._load_data()

        # Calculate stats by difficulty
        by_difficulty = {}
        for q in data["questions"]:
            diff = q["difficulty"]
            if diff not in by_difficulty:
                by_difficulty[diff] = {"total": 0, "completed": 0, "attempts": 0}

            by_difficulty[diff]["total"] += 1
            by_difficulty[diff]["completed"] += 1 if q["completed"] else 0
            by_difficulty[diff]["attempts"] += q["attempts"]

        # Calculate completion rate
        total = len(data["questions"])
        completed = sum(1 for q in data["questions"] if q["completed"])
        completion_rate = (completed / total * 100) if total > 0 else 0

        return {
            "total_questions": total,
            "total_completed": completed,
            "total_attempts": data["metadata"].get("total_attempts", 0),
            "completion_rate": round(completion_rate, 2),
            "by_difficulty": by_difficulty,
            "created_at": data["metadata"].get("created_at"),
            "last_generated": data["metadata"].get("last_generated"),
            "updated_at": data["metadata"].get("updated_at")
        }

    def reset_progress(self) -> bool:
        """
        Reset all progress (attempts and completions)

        Returns:
            True if successful
        """
        data = self._load_data()

        for question in data["questions"]:
            question["attempts"] = 0
            question["completed"] = False
            question["session_ids"] = []
            if "completed_at" in question:
                del question["completed_at"]
            if "last_attempted" in question:
                del question["last_attempted"]

        data["metadata"]["total_attempts"] = 0
        data["metadata"]["total_completed"] = 0

        self._save_data(data)
        return True
