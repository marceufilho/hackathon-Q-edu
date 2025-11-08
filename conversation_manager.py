"""
Conversation Session Manager

Manages teaching sessions with file-based persistence.
Each session tracks the conversation history, current phase, and hint level.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from polya_phases import PolyaPhase
from hint_system import HintLevel, HintEscalation


class SessionManager:
    """Manages conversation sessions with file-based persistence"""

    def __init__(self, sessions_dir: str = "sessions"):
        """
        Initialize the session manager

        Args:
            sessions_dir: Directory to store session files
        """
        self.sessions_dir = sessions_dir
        os.makedirs(sessions_dir, exist_ok=True)

    def create_session(self, problem: str, first_question: str) -> Dict:
        """
        Create a new teaching session

        Args:
            problem: The math problem to solve
            first_question: The first Socratic question

        Returns:
            Session data including session_id
        """
        session_id = str(uuid.uuid4())

        session_data = {
            "session_id": session_id,
            "problem": problem,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "current_phase": PolyaPhase.UNDERSTANDING.name,
            "hint_level": HintLevel.GENTLE.value,
            "conversation": [
                {
                    "role": "teacher",
                    "content": first_question,
                    "phase": PolyaPhase.UNDERSTANDING.name,
                    "hint_level": HintLevel.GENTLE.value,
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "is_complete": False,
            "hint_escalation": {
                "struggle_count": 0,
                "consecutive_struggles": 0
            }
        }

        self._save_session(session_id, session_data)
        return session_data

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve a session by ID

        Args:
            session_id: The session identifier

        Returns:
            Session data or None if not found
        """
        session_path = self._get_session_path(session_id)
        if not os.path.exists(session_path):
            return None

        with open(session_path, 'r') as f:
            return json.load(f)

    def update_session(
        self,
        session_id: str,
        student_response: str,
        teacher_question: str,
        phase: PolyaPhase,
        hint_level: HintLevel,
        is_complete: bool = False
    ) -> Dict:
        """
        Update session with new exchange

        Args:
            session_id: The session identifier
            student_response: Student's latest response
            teacher_question: Teacher's next question
            phase: Current Polya phase
            hint_level: Current hint level
            is_complete: Whether the session is complete

        Returns:
            Updated session data
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Add student response
        session["conversation"].append({
            "role": "student",
            "content": student_response,
            "timestamp": datetime.now().isoformat()
        })

        # Add teacher question
        session["conversation"].append({
            "role": "teacher",
            "content": teacher_question,
            "phase": phase.name,
            "hint_level": hint_level.value,
            "timestamp": datetime.now().isoformat()
        })

        # Update session metadata
        session["current_phase"] = phase.name
        session["hint_level"] = hint_level.value
        session["updated_at"] = datetime.now().isoformat()
        session["is_complete"] = is_complete

        self._save_session(session_id, session)
        return session

    def update_hint_escalation(
        self,
        session_id: str,
        struggle_count: int,
        consecutive_struggles: int
    ):
        """
        Update hint escalation tracking

        Args:
            session_id: The session identifier
            struggle_count: Total struggle count
            consecutive_struggles: Consecutive struggles count
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session["hint_escalation"] = {
            "struggle_count": struggle_count,
            "consecutive_struggles": consecutive_struggles
        }

        self._save_session(session_id, session)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session

        Args:
            session_id: The session identifier

        Returns:
            True if deleted, False if not found
        """
        session_path = self._get_session_path(session_id)
        if os.path.exists(session_path):
            os.remove(session_path)
            return True
        return False

    def list_sessions(self) -> List[Dict]:
        """
        List all sessions with basic metadata

        Returns:
            List of session summaries
        """
        sessions = []
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json'):
                session_id = filename[:-5]  # Remove .json
                session = self.get_session(session_id)
                if session:
                    sessions.append({
                        "session_id": session_id,
                        "problem": session["problem"],
                        "created_at": session["created_at"],
                        "current_phase": session["current_phase"],
                        "is_complete": session.get("is_complete", False),
                        "num_exchanges": len([m for m in session["conversation"]
                                            if m["role"] == "student"])
                    })
        return sorted(sessions, key=lambda x: x["created_at"], reverse=True)

    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """
        Get conversation history for a session

        Args:
            session_id: The session identifier

        Returns:
            List of conversation exchanges
        """
        session = self.get_session(session_id)
        if not session:
            return []

        history = []
        i = 0
        conversation = session["conversation"]

        while i < len(conversation):
            if conversation[i]["role"] == "teacher":
                exchange = {
                    "question": conversation[i]["content"],
                    "phase": conversation[i].get("phase"),
                    "hint_level": conversation[i].get("hint_level"),
                    "timestamp": conversation[i].get("timestamp")
                }

                # Get student response if exists
                if i + 1 < len(conversation) and conversation[i + 1]["role"] == "student":
                    exchange["response"] = conversation[i + 1]["content"]
                    i += 2
                else:
                    i += 1

                history.append(exchange)
            else:
                i += 1

        return history

    def _get_session_path(self, session_id: str) -> str:
        """Get the file path for a session"""
        return os.path.join(self.sessions_dir, f"{session_id}.json")

    def _save_session(self, session_id: str, session_data: Dict):
        """Save session data to file"""
        session_path = self._get_session_path(session_id)
        with open(session_path, 'w') as f:
            json.dump(session_data, f, indent=2)
