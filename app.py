"""
Q-Edu Socratic Math Teacher API

Flask API for the Socratic teaching system using Polya's method.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flasgger import Swagger

from socratic_solver import SocraticTeacher
from conversation_manager import SessionManager
from polya_phases import PolyaPhase
from hint_system import HintLevel, HintEscalation
from question_manager import QuestionManager
from adaptive_engine import AdaptiveEngine
from diagnostic_test import DiagnosticTest
from knowledge_graph_manager import KnowledgeGraphManager
from mastery_tracker import MasteryTracker
from tutor_commentary import TutorCommentary
from solution_generator import SolutionGenerator
from eq_ocr_easyocr import easyocr_math_ocr

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Enable CORS for all routes
CORS(app)

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Q-Edu Socratic Math Teacher API",
        "description": "AI-powered Socratic teaching system using Polya's Method and adaptive hint escalation. Guides students through mathematical problem-solving by asking questions instead of giving direct answers.",
        "version": "1.0.0",
        "contact": {
            "name": "Q-Edu Team",
            "url": "https://github.com/yourusername/q-edu"
        }
    },
    "basePath": "/",
    "schemes": ["http"],
    "tags": [
        {
            "name": "Practice Questions",
            "description": "Generate and manage practice problems"
        },
        {
            "name": "Diagnostic Test",
            "description": "Initial assessment to determine student level"
        },
        {
            "name": "Adaptive Learning",
            "description": "Personalized adaptive learning system"
        },
        {
            "name": "Progress Tracking",
            "description": "Track student progress and mastery"
        },
        {
            "name": "OCR and Solutions",
            "description": "Extract equations from images and generate step-by-step solutions"
        },
        {
            "name": "Teaching Sessions",
            "description": "Manage teaching sessions and interactions"
        },
        {
            "name": "Session Management",
            "description": "View and manage session data"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Initialize components
session_manager = SessionManager()
question_manager = QuestionManager()
knowledge_graph = KnowledgeGraphManager()
teacher = None  # Will initialize per request to handle API key
solution_generator = None  # Will initialize per request to handle API key

# Diagnostic and adaptive instances per student (stored in memory)
diagnostic_sessions = {}
adaptive_sessions = {}


def get_teacher():
    """Get or create teacher instance"""
    global teacher
    if teacher is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        teacher = SocraticTeacher(api_key)
    return teacher


def get_solution_generator():
    """Get or create solution generator instance"""
    global solution_generator
    if solution_generator is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        solution_generator = SolutionGenerator(api_key)
    return solution_generator


@app.route('/api', methods=['GET'])
def api_info():
    """API information
    ---
    tags:
      - Teaching Sessions
    responses:
      200:
        description: API information
        schema:
          type: object
          properties:
            service:
              type: string
              example: Q-Edu Socratic Math Teacher
            version:
              type: string
              example: 1.0.0
            description:
              type: string
            endpoints:
              type: object
    """
    return jsonify({
        "service": "Q-Edu Socratic Math Teacher API",
        "version": "1.0.0",
        "description": "AI-powered Socratic teaching system using Polya's method with adaptive learning",
        "swagger_ui": "http://localhost:5000/docs",
        "documentation": "http://localhost:5000/apispec.json",
        "main_features": {
            "diagnostic_test": "Initial assessment to determine student level",
            "adaptive_learning": "Personalized adaptive learning system",
            "progress_tracking": "Track student progress and mastery",
            "socratic_teaching": "Learn through guided questions",
            "progressive_hints": "3-level hint system (gentle, specific, directive)",
            "ocr_extraction": "Extract math equations from images",
            "solution_generation": "Generate step-by-step solutions with AI"
        },
        "endpoints": {
            "POST /start": "Start a new Socratic teaching session",
            "POST /respond": "Submit student response and get next question",
            "POST /diagnostic/start": "Start diagnostic test",
            "POST /adaptive/start": "Start adaptive learning session",
            "GET /progress/<student_id>": "Get student progress",
            "GET /topics/available": "Get all available topics",
            "POST /adaptive/<student_id>/hint": "Get progressive hints",
            "POST /ocr/extract": "Extract equation from image using OCR",
            "POST /solution/generate": "Generate step-by-step solution"
        }
    })


# ============================================================================
# PRACTICE QUESTIONS ENDPOINTS
# ============================================================================

@app.route('/questions/generate', methods=['POST'])
def generate_questions():
    """Generate new practice questions
    ---
    tags:
      - Practice Questions
    parameters:
      - name: body
        in: body
        required: false
        description: Generation parameters
        schema:
          type: object
          properties:
            count:
              type: integer
              example: 10
              description: Number of questions to generate (default 10)
            difficulty:
              type: string
              example: "medium"
              enum: [easy, medium, hard]
              description: Difficulty level (default mixed)
            topic:
              type: string
              example: "Equações Lineares"
              description: Topic to generate questions for (e.g., "Equações Lineares", "Operações Básicas")
    responses:
      201:
        description: Questions generated successfully
        schema:
          type: object
          properties:
            message:
              type: string
            count:
              type: integer
            questions:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  problem:
                    type: string
                    example: "Solve for x: 2x + 5 = 13"
                  difficulty:
                    type: string
                  type:
                    type: string
                  topic:
                    type: string
      400:
        description: Bad request - invalid topic
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        data = request.get_json() or {}
        count = data.get('count', 10)
        difficulty = data.get('difficulty')
        topic = data.get('topic')

        questions = question_manager.generate_questions(count, difficulty, topic)

        return jsonify({
            "message": f"Generated {len(questions)} questions successfully",
            "count": len(questions),
            "questions": questions
        }), 201

    except ValueError as e:
        # Catch invalid topic errors
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/questions', methods=['GET'])
def list_questions():
    """List all practice questions
    ---
    tags:
      - Practice Questions
    parameters:
      - name: difficulty
        in: query
        type: string
        required: false
        description: Filter by difficulty
        enum: [easy, medium, hard]
      - name: completed
        in: query
        type: boolean
        required: false
        description: Filter by completion status
      - name: limit
        in: query
        type: integer
        required: false
        description: Maximum number of questions to return
      - name: topic
        in: query
        type: string
        required: false
        description: Filter by topic (e.g., "Equações Lineares", "Operações Básicas")
    responses:
      200:
        description: List of questions
        schema:
          type: object
          properties:
            questions:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  problem:
                    type: string
                  difficulty:
                    type: string
                  type:
                    type: string
                  topic:
                    type: string
                  attempts:
                    type: integer
                  completed:
                    type: boolean
            count:
              type: integer
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        difficulty = request.args.get('difficulty')
        completed = request.args.get('completed')
        limit = request.args.get('limit', type=int)
        topic = request.args.get('topic')

        # Convert completed string to boolean
        if completed is not None:
            completed = completed.lower() in ['true', '1', 'yes']

        questions = question_manager.list_questions(difficulty, completed, limit, topic)

        return jsonify({
            "questions": questions,
            "count": len(questions)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/questions/<question_id>', methods=['GET'])
def get_question(question_id):
    """Get a specific question
    ---
    tags:
      - Practice Questions
    parameters:
      - name: question_id
        in: path
        type: string
        required: true
        description: Question ID
    responses:
      200:
        description: Question details
        schema:
          type: object
          properties:
            id:
              type: string
            problem:
              type: string
              example: "Solve for x: 2x + 5 = 13"
            equation:
              type: string
            answer:
              type: number
            steps:
              type: array
              items:
                type: string
            difficulty:
              type: string
            type:
              type: string
            topic:
              type: string
            attempts:
              type: integer
            completed:
              type: boolean
            session_ids:
              type: array
              items:
                type: string
      404:
        description: Question not found
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        question = question_manager.get_question(question_id)
        if not question:
            return jsonify({"error": f"Question {question_id} not found"}), 404

        return jsonify(question), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/questions/<question_id>/start', methods=['POST'])
def start_question_session(question_id):
    """Start a teaching session with a specific question
    ---
    tags:
      - Practice Questions
    parameters:
      - name: question_id
        in: path
        type: string
        required: true
        description: Question ID to work on
    responses:
      201:
        description: Teaching session started
        schema:
          type: object
          properties:
            session_id:
              type: string
            question_id:
              type: string
            problem:
              type: string
            question:
              type: string
              description: First Socratic question from teacher
            phase:
              type: string
            hint_level:
              type: integer
      404:
        description: Question not found
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        # Get the question
        question = question_manager.get_question(question_id)
        if not question:
            return jsonify({"error": f"Question {question_id} not found"}), 404

        # Generate first Socratic question
        teacher_instance = get_teacher()
        first_question = teacher_instance.generate_initial_question(question["problem"])

        # Create teaching session
        session = session_manager.create_session(question["problem"], first_question)

        # Mark question as attempted
        question_manager.mark_attempted(question_id, session["session_id"])

        return jsonify({
            "session_id": session["session_id"],
            "question_id": question_id,
            "problem": question["problem"],
            "difficulty": question["difficulty"],
            "question": first_question,
            "phase": PolyaPhase.UNDERSTANDING.name,
            "hint_level": HintLevel.GENTLE.value,
            "created_at": session["created_at"]
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/questions/stats', methods=['GET'])
def get_question_stats():
    """Get question bank statistics
    ---
    tags:
      - Practice Questions
    responses:
      200:
        description: Statistics about the question bank
        schema:
          type: object
          properties:
            total_questions:
              type: integer
            total_completed:
              type: integer
            total_attempts:
              type: integer
            completion_rate:
              type: number
            by_difficulty:
              type: object
              properties:
                easy:
                  type: object
                  properties:
                    total:
                      type: integer
                    completed:
                      type: integer
                    attempts:
                      type: integer
                medium:
                  type: object
                hard:
                  type: object
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        stats = question_manager.get_stats()
        return jsonify(stats), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/questions/<question_id>', methods=['DELETE'])
def delete_question(question_id):
    """Delete a practice question
    ---
    tags:
      - Practice Questions
    parameters:
      - name: question_id
        in: path
        type: string
        required: true
        description: Question ID to delete
    responses:
      200:
        description: Question deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Question not found
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        success = question_manager.delete_question(question_id)
        if not success:
            return jsonify({"error": f"Question {question_id} not found"}), 404

        return jsonify({"message": "Question deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# DIAGNOSTIC TEST ENDPOINTS
# ============================================================================

@app.route('/diagnostic/start', methods=['POST'])
def start_diagnostic():
    """Start a diagnostic test for a student
    ---
    tags:
      - Diagnostic Test
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - student_id
          properties:
            student_id:
              type: string
              example: "student_123"
            questions_per_topic:
              type: integer
              example: 3
              description: Number of questions per diagnostic topic
    responses:
      201:
        description: Diagnostic test started
      500:
        description: Error starting diagnostic
    """
    try:
        data = request.get_json()
        student_id = data.get('student_id')

        if not student_id:
            return jsonify({"error": "student_id is required"}), 400

        questions_per_topic = data.get('questions_per_topic', 3)

        # Create diagnostic test instance
        diagnostic = DiagnosticTest(student_id)
        result = diagnostic.generate_diagnostic_test(questions_per_topic)

        # Store in session
        diagnostic_sessions[student_id] = diagnostic

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/diagnostic/<student_id>/next', methods=['GET'])
def get_diagnostic_question(student_id):
    """Get next diagnostic question
    ---
    tags:
      - Diagnostic Test
    parameters:
      - name: student_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Next question or completion message
      404:
        description: Diagnostic session not found
      500:
        description: Error
    """
    try:
        diagnostic = diagnostic_sessions.get(student_id)

        if not diagnostic:
            return jsonify({"error": "Diagnostic session not found. Call /diagnostic/start first"}), 404

        result = diagnostic.get_next_question()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/diagnostic/<student_id>/submit', methods=['POST'])
def submit_diagnostic_answer(student_id):
    """Submit answer to diagnostic question
    ---
    tags:
      - Diagnostic Test
    parameters:
      - name: student_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - question_id
            - answer
          properties:
            question_id:
              type: string
            answer:
              type: string
    responses:
      200:
        description: Answer processed
      404:
        description: Diagnostic session not found
      500:
        description: Error
    """
    try:
        diagnostic = diagnostic_sessions.get(student_id)

        if not diagnostic:
            return jsonify({"error": "Diagnostic session not found"}), 404

        data = request.get_json()
        question_id = data.get('question_id')
        answer = data.get('answer')

        if not question_id or answer is None:
            return jsonify({"error": "question_id and answer are required"}), 400

        result = diagnostic.submit_answer(question_id, answer)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ADAPTIVE LEARNING ENDPOINTS
# ============================================================================

@app.route('/adaptive/start', methods=['POST'])
def start_adaptive_session():
    """Start an adaptive learning session
    ---
    tags:
      - Adaptive Learning
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - student_id
          properties:
            student_id:
              type: string
              example: "student_123"
            learning_path:
              type: string
              enum: [beginner, intermediate, advanced]
              description: Optional learning path
    responses:
      201:
        description: Adaptive session started
      500:
        description: Error
    """
    try:
        data = request.get_json()
        student_id = data.get('student_id')

        if not student_id:
            return jsonify({"error": "student_id is required"}), 400

        learning_path = data.get('learning_path')

        # Create adaptive engine
        api_key = os.environ.get("GEMINI_API_KEY")
        engine = AdaptiveEngine(student_id, api_key=api_key)

        result = engine.start_new_session(learning_path)

        # Store in session
        adaptive_sessions[student_id] = engine

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/adaptive/<student_id>/next', methods=['GET'])
def get_adaptive_question(student_id):
    """Get next adaptive question
    ---
    tags:
      - Adaptive Learning
    parameters:
      - name: student_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Next adaptive question
      404:
        description: Adaptive session not found
      500:
        description: Error
    """
    try:
        engine = adaptive_sessions.get(student_id)

        if not engine:
            return jsonify({"error": "Adaptive session not found. Call /adaptive/start first"}), 404

        question = engine.get_next_question()
        return jsonify(question), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/adaptive/<student_id>/submit', methods=['POST'])
def submit_adaptive_answer(student_id):
    """Submit answer to adaptive question
    ---
    tags:
      - Adaptive Learning
    parameters:
      - name: student_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - question_id
            - question
            - student_answer
            - correct_answer
            - solution_steps
            - concepts_tested
          properties:
            question_id:
              type: string
            question:
              type: string
            student_answer:
              type: string
            correct_answer:
              type: string
            solution_steps:
              type: array
              items:
                type: string
            concepts_tested:
              type: array
              items:
                type: string
    responses:
      200:
        description: Answer processed with feedback
      404:
        description: Adaptive session not found
      500:
        description: Error
    """
    try:
        engine = adaptive_sessions.get(student_id)

        if not engine:
            return jsonify({"error": "Adaptive session not found"}), 404

        data = request.get_json()

        required_fields = ['question_id', 'question', 'student_answer', 'correct_answer', 'solution_steps', 'concepts_tested']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        result = engine.submit_answer(
            question_id=data['question_id'],
            question=data['question'],
            student_answer=data['student_answer'],
            correct_answer=data['correct_answer'],
            solution_steps=data['solution_steps'],
            concepts_tested=data['concepts_tested']
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/adaptive/<student_id>/change-topic', methods=['POST'])
def change_adaptive_topic(student_id):
    """Change to a different topic
    ---
    tags:
      - Adaptive Learning
    parameters:
      - name: student_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - topic_id
          properties:
            topic_id:
              type: string
              example: "equacoes_lineares_uma_etapa"
    responses:
      200:
        description: Topic changed successfully
      404:
        description: Adaptive session not found
      500:
        description: Error
    """
    try:
        engine = adaptive_sessions.get(student_id)

        if not engine:
            return jsonify({"error": "Adaptive session not found"}), 404

        data = request.get_json()
        topic_id = data.get('topic_id')

        if not topic_id:
            return jsonify({"error": "topic_id is required"}), 400

        result = engine.advance_to_topic(topic_id)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/topics/available', methods=['GET'])
def get_available_topics():
    """Get list of available topics with question generators
    ---
    tags:
      - Adaptive Learning
    responses:
      200:
        description: List of available topics
        schema:
          type: object
          properties:
            topics:
              type: array
              items:
                type: object
                properties:
                  topic_id:
                    type: string
                  name:
                    type: string
                  description:
                    type: string
                  difficulty:
                    type: integer
                  has_questions:
                    type: boolean
      500:
        description: Error
    """
    try:
        # Get all topics from knowledge graph
        topics_list = []

        for topic_id, topic_data in knowledge_graph.topics.items():
            topics_list.append({
                "topic_id": topic_id,
                "name": topic_data["name"],
                "description": topic_data["description"],
                "difficulty": topic_data["difficulty"],
                "prerequisites": topic_data.get("prerequisites", []),
                "has_questions": True  # All topics have question generators now
            })

        # Sort by difficulty
        topics_list.sort(key=lambda t: t["difficulty"])

        return jsonify({"topics": topics_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/adaptive/<student_id>/hint', methods=['POST'])
def get_adaptive_hint(student_id):
    """Get progressive hint for current question
    ---
    tags:
      - Adaptive Learning
    parameters:
      - name: student_id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - question
            - hint_level
          properties:
            question:
              type: object
              description: Current question data
            hint_level:
              type: integer
              description: Hint level (1, 2, or 3)
              minimum: 1
              maximum: 3
    responses:
      200:
        description: Hint generated
        schema:
          type: object
          properties:
            hint:
              type: string
            level:
              type: integer
            level_name:
              type: string
            max_level:
              type: integer
      400:
        description: Bad request
      500:
        description: Error
    """
    try:
        data = request.get_json()

        if not data or 'question' not in data or 'hint_level' not in data:
            return jsonify({"error": "question and hint_level are required"}), 400

        question = data['question']
        hint_level = data['hint_level']

        # Validate hint level
        if hint_level not in [1, 2, 3]:
            return jsonify({"error": "hint_level must be 1, 2, or 3"}), 400

        # Generate progressive hint
        hint_data = TutorCommentary.generate_progressive_hint(question, hint_level)

        return jsonify(hint_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# PROGRESS TRACKING ENDPOINTS
# ============================================================================

@app.route('/progress/<student_id>', methods=['GET'])
def get_student_progress(student_id):
    """Get overall student progress
    ---
    tags:
      - Progress Tracking
    parameters:
      - name: student_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Student progress summary
      500:
        description: Error
    """
    try:
        engine = adaptive_sessions.get(student_id)

        if not engine:
            # Create temporary engine just to get progress
            api_key = os.environ.get("GEMINI_API_KEY")
            engine = AdaptiveEngine(student_id, api_key=api_key)

        progress = engine.get_progress_summary()
        return jsonify(progress), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/progress/<student_id>/recommendations', methods=['GET'])
def get_recommended_topics(student_id):
    """Get recommended topics for student
    ---
    tags:
      - Progress Tracking
    parameters:
      - name: student_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Recommended topics
      500:
        description: Error
    """
    try:
        engine = adaptive_sessions.get(student_id)

        if not engine:
            # Create temporary engine
            api_key = os.environ.get("GEMINI_API_KEY")
            engine = AdaptiveEngine(student_id, api_key=api_key)

        recommendations = engine.get_recommended_topics()
        return jsonify({"recommendations": recommendations}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/progress/<student_id>/topic/<topic_id>', methods=['GET'])
def get_topic_progress(student_id, topic_id):
    """Get progress for a specific topic
    ---
    tags:
      - Progress Tracking
    parameters:
      - name: student_id
        in: path
        type: string
        required: true
      - name: topic_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Topic progress details
      500:
        description: Error
    """
    try:
        tracker = MasteryTracker(student_id)
        topic_progress = tracker.get_topic_progress(topic_id)

        # Get mastery info
        topic_data = knowledge_graph.get_topic(topic_id)
        if topic_data:
            mastery_info = tracker.calculate_mastery(
                topic_id,
                topic_data['mastery_threshold'],
                topic_data['min_questions']
            )
        else:
            mastery_info = {"error": "Topic not found"}

        return jsonify({
            "topic_id": topic_id,
            "topic_name": topic_data['name'] if topic_data else "Unknown",
            "progress": topic_progress,
            "mastery": mastery_info
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# OCR AND SOLUTION GENERATION ENDPOINTS
# ============================================================================

@app.route('/ocr/extract', methods=['POST'])
def extract_equation_ocr():
    """Extract math equation from image using OCR
    ---
    tags:
      - OCR and Solutions
    consumes:
      - multipart/form-data
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: Image file containing math equation
    responses:
      200:
        description: Equation extracted successfully
        schema:
          type: object
          properties:
            text:
              type: string
              example: "2x + 5 = 13"
              description: Extracted equation text
            backend:
              type: string
              example: "easyocr"
            confidence:
              type: number
              example: 0.95
              description: OCR confidence score (0-1)
      400:
        description: Bad request - no image provided
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        # Check if image file is in request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided. Use 'image' field in multipart/form-data"}), 400

        image_file = request.files['image']

        if image_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        # Read image bytes
        image_bytes = image_file.read()

        if not image_bytes:
            return jsonify({"error": "Empty image file"}), 400

        # Perform OCR
        ocr_result = easyocr_math_ocr(image_bytes)

        return jsonify({
            "text": ocr_result.text,
            "backend": ocr_result.backend,
            "confidence": ocr_result.confidence
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/solution/generate', methods=['POST'])
def generate_solution():
    """Generate step-by-step solution for a math problem
    ---
    tags:
      - OCR and Solutions
    parameters:
      - name: body
        in: body
        required: true
        description: Math problem to solve
        schema:
          type: object
          required:
            - problem
          properties:
            problem:
              type: string
              example: "Resolva para x: 2x + 5 = 13"
              description: Math problem in Portuguese or English
    responses:
      200:
        description: Solution generated successfully
        schema:
          type: object
          properties:
            problem:
              type: string
              example: "Resolva para x: 2x + 5 = 13"
            answer:
              type: string
              example: "x = 4"
            steps:
              type: array
              items:
                type: string
              example: ["Passo 1: Subtraia 5 de ambos os lados", "Passo 2: Divida por 2"]
            concepts:
              type: array
              items:
                type: string
              example: ["Equações lineares", "Operações inversas"]
            explanation:
              type: string
              example: "Para resolver uma equação linear, isolamos a variável aplicando operações inversas."
      400:
        description: Bad request - invalid problem
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        data = request.get_json()

        if not data or 'problem' not in data:
            return jsonify({"error": "Missing 'problem' in request body"}), 400

        problem = data['problem'].strip()

        # Validate problem
        generator = get_solution_generator()
        is_valid, message = generator.validate_problem(problem)

        if not is_valid:
            return jsonify({"error": message}), 400

        # Generate solution
        solution = generator.generate_solution(problem)

        # Check if there was an error during generation
        if 'error' in solution:
            return jsonify(solution), 500

        return jsonify(solution), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# TEACHING SESSION ENDPOINTS
# ============================================================================

@app.route('/start', methods=['POST'])
def start_session():
    """Start a new teaching session
    ---
    tags:
      - Teaching Sessions
    parameters:
      - name: body
        in: body
        required: true
        description: Math problem to solve
        schema:
          type: object
          required:
            - problem
          properties:
            problem:
              type: string
              example: "Solve for x: 2x + 5 = 13"
              description: The math problem you want help solving
    responses:
      201:
        description: Session created successfully
        schema:
          type: object
          properties:
            session_id:
              type: string
              example: "438ecde3-cad0-494c-94a3-79895969216b"
            problem:
              type: string
              example: "Solve for x: 2x + 5 = 13"
            question:
              type: string
              example: "What is this equation asking you to find?"
            phase:
              type: string
              example: "UNDERSTANDING"
            hint_level:
              type: integer
              example: 0
            created_at:
              type: string
              format: date-time
      400:
        description: Bad request - missing or invalid problem
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        data = request.get_json()

        if not data or 'problem' not in data:
            return jsonify({"error": "Missing 'problem' in request body"}), 400

        problem = data['problem'].strip()
        if not problem:
            return jsonify({"error": "Problem cannot be empty"}), 400

        # Generate first question
        teacher_instance = get_teacher()
        first_question = teacher_instance.generate_initial_question(problem)

        # Create session
        session = session_manager.create_session(problem, first_question)

        return jsonify({
            "session_id": session["session_id"],
            "problem": problem,
            "question": first_question,
            "phase": PolyaPhase.UNDERSTANDING.name,
            "hint_level": HintLevel.GENTLE.value,
            "created_at": session["created_at"]
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/respond', methods=['POST'])
def respond():
    """Submit student response and get next question
    ---
    tags:
      - Teaching Sessions
    parameters:
      - name: body
        in: body
        required: true
        description: Student's response to the previous question
        schema:
          type: object
          required:
            - session_id
            - response
          properties:
            session_id:
              type: string
              example: "438ecde3-cad0-494c-94a3-79895969216b"
              description: Session ID from /start endpoint
            response:
              type: string
              example: "It's asking me to find the value of x"
              description: Your answer to the teacher's question
    responses:
      200:
        description: Next question generated successfully
        schema:
          type: object
          properties:
            question:
              type: string
              example: "Good! What information does the equation give you?"
            phase:
              type: string
              example: "UNDERSTANDING"
              enum: [UNDERSTANDING, PLANNING, EXECUTION, REVIEW]
            hint_level:
              type: integer
              example: 0
              description: Current hint level (0=gentle, 1=specific, 2=directive)
            is_complete:
              type: boolean
              example: false
              description: Whether all phases are complete
            encouragement:
              type: string
              example: "Let me give you a bit more direction to help you out."
              description: Optional encouragement when hint level changes
            message:
              type: string
              description: Completion message when session is done
      400:
        description: Bad request - missing session_id or response
        schema:
          type: object
          properties:
            error:
              type: string
      404:
        description: Session not found
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        data = request.get_json()

        if not data or 'session_id' not in data or 'response' not in data:
            return jsonify({"error": "Missing 'session_id' or 'response' in request body"}), 400

        session_id = data['session_id']
        student_response = data['response'].strip()

        if not student_response:
            return jsonify({"error": "Response cannot be empty"}), 400

        # Get session
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({"error": f"Session {session_id} not found"}), 404

        if session.get("is_complete"):
            return jsonify({
                "message": "This session is already complete",
                "is_complete": True
            }), 200

        # Get current state
        current_phase = PolyaPhase[session["current_phase"]]
        current_hint_level = HintLevel(session["hint_level"])

        # Update hint escalation based on response
        hint_escalation = HintEscalation()
        hint_escalation.struggle_count = session["hint_escalation"]["struggle_count"]
        hint_escalation.consecutive_struggles = session["hint_escalation"]["consecutive_struggles"]
        hint_escalation.current_level = current_hint_level

        updated_hint_level = hint_escalation.update_from_response(student_response)

        # Update hint escalation in session
        session_manager.update_hint_escalation(
            session_id,
            hint_escalation.struggle_count,
            hint_escalation.consecutive_struggles
        )

        # Get conversation history
        conversation_history = session_manager.get_conversation_history(session_id)

        # Generate next question
        teacher_instance = get_teacher()
        result = teacher_instance.generate_next_question(
            problem=session["problem"],
            current_phase=current_phase,
            hint_level=updated_hint_level,
            conversation_history=conversation_history,
            student_response=student_response
        )

        # Update session
        session_manager.update_session(
            session_id=session_id,
            student_response=student_response,
            teacher_question=result["question"],
            phase=result["phase"],
            hint_level=result["hint_level"],
            is_complete=result["is_complete"]
        )

        response_data = {
            "question": result["question"],
            "phase": result["phase"].name,
            "hint_level": result["hint_level"].value,
            "is_complete": result["is_complete"]
        }

        # Add encouragement if hint level changed
        if updated_hint_level != current_hint_level:
            from hint_system import HintTemplates
            response_data["encouragement"] = HintTemplates.get_encouragement(updated_hint_level)

        # Add completion message if done
        if result["is_complete"]:
            response_data["message"] = "Great work! You've completed all phases of problem solving."

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details and conversation history
    ---
    tags:
      - Session Management
    parameters:
      - name: session_id
        in: path
        type: string
        required: true
        description: Session ID
        example: "438ecde3-cad0-494c-94a3-79895969216b"
    responses:
      200:
        description: Session details retrieved successfully
        schema:
          type: object
          properties:
            session_id:
              type: string
            problem:
              type: string
              example: "Solve for x: 2x + 5 = 13"
            current_phase:
              type: string
              example: "PLANNING"
            hint_level:
              type: integer
              example: 1
            is_complete:
              type: boolean
              example: false
            conversation:
              type: array
              items:
                type: object
                properties:
                  role:
                    type: string
                    enum: [teacher, student]
                  content:
                    type: string
                  phase:
                    type: string
                  hint_level:
                    type: integer
                  timestamp:
                    type: string
            created_at:
              type: string
              format: date-time
            updated_at:
              type: string
              format: date-time
      404:
        description: Session not found
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({"error": f"Session {session_id} not found"}), 404

        # Format conversation for easier reading
        formatted_conversation = []
        for msg in session["conversation"]:
            formatted_msg = {
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg.get("timestamp")
            }
            if msg["role"] == "teacher":
                formatted_msg["phase"] = msg.get("phase")
                formatted_msg["hint_level"] = msg.get("hint_level")
            formatted_conversation.append(formatted_msg)

        return jsonify({
            "session_id": session["session_id"],
            "problem": session["problem"],
            "current_phase": session["current_phase"],
            "hint_level": session["hint_level"],
            "is_complete": session.get("is_complete", False),
            "conversation": formatted_conversation,
            "created_at": session["created_at"],
            "updated_at": session["updated_at"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a teaching session
    ---
    tags:
      - Session Management
    parameters:
      - name: session_id
        in: path
        type: string
        required: true
        description: Session ID to delete
        example: "438ecde3-cad0-494c-94a3-79895969216b"
    responses:
      200:
        description: Session deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Session deleted successfully"
      404:
        description: Session not found
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        success = session_manager.delete_session(session_id)
        if not success:
            return jsonify({"error": f"Session {session_id} not found"}), 404

        return jsonify({"message": "Session deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/sessions', methods=['GET'])
def list_sessions():
    """List all teaching sessions
    ---
    tags:
      - Session Management
    responses:
      200:
        description: List of all sessions
        schema:
          type: object
          properties:
            sessions:
              type: array
              items:
                type: object
                properties:
                  session_id:
                    type: string
                    example: "438ecde3-cad0-494c-94a3-79895969216b"
                  problem:
                    type: string
                    example: "Solve for x: 2x + 5 = 13"
                  current_phase:
                    type: string
                    example: "EXECUTION"
                  is_complete:
                    type: boolean
                    example: false
                  created_at:
                    type: string
                    format: date-time
                  num_exchanges:
                    type: integer
                    example: 5
                    description: Number of student responses
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        sessions = session_manager.list_sessions()
        return jsonify({"sessions": sessions}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Check for API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not found in environment variables")
        print("Please create a .env file with: GEMINI_API_KEY=your_key_here")
        exit(1)

    print("=" * 60)
    print("Q-Edu Socratic Math Teacher API")
    print("=" * 60)
    print("\nServer is starting...")
    print(f"\n   Swagger UI:   http://localhost:5000/docs")
    print(f"   API Info:     http://localhost:5000/api")
    print(f"   OpenAPI:      http://localhost:5000/apispec.json")
    print("\nAPI Features:")
    print("  * Diagnostic Test      - Initial assessment")
    print("  * Adaptive Learning    - Personalized practice")
    print("  * Progress Tracking    - Student progress monitoring")
    print("  * Socratic Chat        - Learn through guided questions")
    print("  * Progressive Hints    - 3-level hint system")
    print("  * AI Tutor             - Contextual feedback and guidance")
    print("\n" + "=" * 60)
    print("API is ready at http://localhost:5000")
    print("View API docs at http://localhost:5000/docs")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
