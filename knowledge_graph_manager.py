"""
Knowledge Graph Manager

Gerencia o grafo de conhecimento e navegação entre tópicos.
"""

import json
from typing import Dict, List, Set, Optional


class KnowledgeGraphManager:
    """Gerenciador do grafo de conhecimento"""

    def __init__(self, graph_file: str = "knowledge_graph.json"):
        """
        Initialize knowledge graph manager

        Args:
            graph_file: Path to knowledge graph JSON file
        """
        self.graph_file = graph_file
        self.graph = self._load_graph()
        self.topics = self.graph["topics"]

    def _load_graph(self) -> Dict:
        """Load knowledge graph from file"""
        with open(self.graph_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_topic(self, topic_id: str) -> Optional[Dict]:
        """
        Get topic information

        Args:
            topic_id: Topic identifier

        Returns:
            Topic data or None if not found
        """
        return self.topics.get(topic_id)

    def get_prerequisites(self, topic_id: str) -> List[str]:
        """
        Get prerequisites for a topic

        Args:
            topic_id: Topic identifier

        Returns:
            List of prerequisite topic IDs
        """
        topic = self.get_topic(topic_id)
        if not topic:
            return []
        return topic.get("prerequisites", [])

    def get_all_prerequisites(self, topic_id: str) -> Set[str]:
        """
        Get all prerequisites recursively (transitive closure)

        Args:
            topic_id: Topic identifier

        Returns:
            Set of all prerequisite topic IDs
        """
        all_prereqs = set()
        to_process = [topic_id]
        processed = set()

        while to_process:
            current = to_process.pop(0)
            if current in processed:
                continue

            processed.add(current)
            prereqs = self.get_prerequisites(current)

            for prereq in prereqs:
                if prereq not in all_prereqs:
                    all_prereqs.add(prereq)
                    to_process.append(prereq)

        return all_prereqs

    def get_dependent_topics(self, topic_id: str) -> List[str]:
        """
        Get topics that depend on this topic

        Args:
            topic_id: Topic identifier

        Returns:
            List of topic IDs that have this as prerequisite
        """
        dependents = []
        for tid, topic in self.topics.items():
            if topic_id in topic.get("prerequisites", []):
                dependents.append(tid)
        return dependents

    def can_start_topic(self, topic_id: str, mastered_topics: Set[str]) -> bool:
        """
        Check if student can start a topic based on mastered prerequisites

        Args:
            topic_id: Topic to check
            mastered_topics: Set of mastered topic IDs

        Returns:
            True if all prerequisites are mastered
        """
        prereqs = set(self.get_prerequisites(topic_id))
        return prereqs.issubset(mastered_topics)

    def get_next_topics(self, mastered_topics: Set[str]) -> List[str]:
        """
        Get recommended next topics based on what's been mastered

        Args:
            mastered_topics: Set of mastered topic IDs

        Returns:
            List of topic IDs that can be started now
        """
        available = []
        for topic_id in self.topics.keys():
            if topic_id not in mastered_topics:
                if self.can_start_topic(topic_id, mastered_topics):
                    available.append(topic_id)

        # Sort by difficulty
        available.sort(key=lambda tid: self.topics[tid]["difficulty"])
        return available

    def get_learning_path(self, path_name: str) -> Optional[Dict]:
        """
        Get predefined learning path

        Args:
            path_name: Name of the path (beginner, intermediate, advanced)

        Returns:
            Learning path data or None
        """
        return self.graph.get("learning_paths", {}).get(path_name)

    def find_prerequisite_gap(self, topic_id: str, mastered_topics: Set[str]) -> List[str]:
        """
        Find which prerequisites are missing for a topic

        Args:
            topic_id: Topic to check
            mastered_topics: Set of mastered topic IDs

        Returns:
            List of missing prerequisite topic IDs
        """
        all_prereqs = self.get_all_prerequisites(topic_id)
        missing = all_prereqs - mastered_topics

        # Sort by difficulty (easier first)
        missing_list = list(missing)
        missing_list.sort(key=lambda tid: self.topics.get(tid, {}).get("difficulty", 99))

        return missing_list

    def get_topic_concepts(self, topic_id: str) -> List[str]:
        """
        Get concepts covered by a topic

        Args:
            topic_id: Topic identifier

        Returns:
            List of concept IDs
        """
        topic = self.get_topic(topic_id)
        if not topic:
            return []
        return topic.get("concepts", [])

    def find_topic_by_concept(self, concept: str) -> Optional[str]:
        """
        Find which topic covers a specific concept

        Args:
            concept: Concept identifier

        Returns:
            Topic ID or None
        """
        for topic_id, topic in self.topics.items():
            if concept in topic.get("concepts", []):
                return topic_id
        return None

    def get_diagnostic_topics(self) -> List[str]:
        """
        Get topics to include in diagnostic test

        Returns:
            List of topic IDs for diagnostic
        """
        return self.graph.get("diagnostic_topics", [])

    def get_mastery_threshold(self, topic_id: str) -> float:
        """
        Get mastery threshold for a topic

        Args:
            topic_id: Topic identifier

        Returns:
            Mastery threshold (0.0 - 1.0)
        """
        topic = self.get_topic(topic_id)
        if not topic:
            return 0.75  # Default
        return topic.get("mastery_threshold", 0.75)

    def get_min_questions(self, topic_id: str) -> int:
        """
        Get minimum questions needed for mastery assessment

        Args:
            topic_id: Topic identifier

        Returns:
            Minimum number of questions
        """
        topic = self.get_topic(topic_id)
        if not topic:
            return 5  # Default
        return topic.get("min_questions", 5)

    def get_topic_path(self, from_topic: str, to_topic: str) -> List[str]:
        """
        Find shortest path between two topics

        Args:
            from_topic: Starting topic
            to_topic: Target topic

        Returns:
            List of topic IDs forming the path
        """
        # Simple BFS to find path
        queue = [(from_topic, [from_topic])]
        visited = {from_topic}

        while queue:
            current, path = queue.pop(0)

            if current == to_topic:
                return path

            # Check dependent topics
            for dependent in self.get_dependent_topics(current):
                if dependent not in visited:
                    visited.add(dependent)
                    queue.append((dependent, path + [dependent]))

        return []  # No path found
