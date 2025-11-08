# Q-Edu: Adaptive Math Learning API

An AI-powered adaptive learning system that provides personalized math education through **Socratic teaching**, **diagnostic assessment**, and **intelligent tutoring**. The system uses Polya's Method, adaptive difficulty adjustment, and progressive hint systems to guide students through their learning journey.

## Features

### Core Learning Systems
- **Diagnostic Testing**: Initial assessment to determine student level across 11 math topics
- **Adaptive Learning Engine**: Automatically adjusts difficulty and identifies knowledge gaps
- **Knowledge Graph**: 11 interconnected math topics with prerequisite dependencies
- **Mastery Tracking**: Monitors student progress with accuracy and conceptual error analysis
- **Error Analysis**: AI-powered classification of student mistakes (conceptual, procedural, arithmetic, careless)

### Teaching Methods
- **Polya's 4-Phase Method**: Guides students through Understanding → Planning → Execution → Review
- **Socratic Questioning**: Never gives direct answers; asks probing questions instead
- **Progressive Hints (3 Levels)**:
  - Level 1 (Gentle): Open-ended guiding questions
  - Level 2 (Specific): Pointed hints with context
  - Level 3 (Directive): Step-by-step guidance with answer reveal
- **AI Tutor Commentary**: Contextual feedback, encouragement, and explanations in Portuguese

### Technical Features
- **RESTful API**: Complete backend API with Swagger documentation
- **Session Persistence**: All progress and conversations saved
- **Question Generation**: Dynamic question creation for all topics and difficulty levels

## Prerequisites

- Python 3.12 or higher
- Google Gemini API key
- Flask for API server

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd q-edu
```

2. Install dependencies using uv (recommended) or pip:
```bash
# Using uv
uv sync

# Or using pip
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

> **Note**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Quick Start

### Start the API Server

```bash
uv run python app.py
```

The server will start at `http://localhost:5000`

### Interactive API Documentation (Swagger UI)

Visit **http://localhost:5000/docs** in your browser to access the interactive Swagger UI where you can:
- See all available endpoints
- Try out the API directly in your browser
- View request/response schemas
- Test with example data

**No code needed** - just click "Try it out" on any endpoint!

### Example: Teaching a Linear Equation

See `example_client.py` for a complete example. Here's a quick overview:

```python
import requests

# Start a new teaching session
response = requests.post('http://localhost:5000/start', json={
    "problem": "Solve for x: 2x + 5 = 13"
})
session = response.json()
print(f"Teacher: {session['question']}")
# Output: "What is this equation asking you to find?"

# Submit student response
response = requests.post('http://localhost:5000/respond', json={
    "session_id": session['session_id'],
    "response": "It's asking me to find the value of x"
})
result = response.json()
print(f"Teacher: {result['question']}")
# Output: "Good! What information does the equation give you?"
```

## API Endpoints

> **Interactive Documentation**: Visit [http://localhost:5000/docs](http://localhost:5000/docs) for Swagger UI with interactive testing
>
> **API Info**: GET [http://localhost:5000/api](http://localhost:5000/api) for endpoint overview

---

## 📋 Diagnostic Test Endpoints

### `POST /diagnostic/start`
**Description**: Start a diagnostic test to assess student's level across all topics

**Request:**
```json
{
  "student_id": "student_123",
  "questions_per_topic": 2
}
```

**Response:**
```json
{
  "student_id": "student_123",
  "total_questions": 22,
  "topics_covered": 11,
  "message": "Diagnostic test started. Use /diagnostic/{student_id}/next to get questions."
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/diagnostic/start \
  -H "Content-Type: application/json" \
  -d '{"student_id": "aluno_001", "questions_per_topic": 2}'
```

---

### `GET /diagnostic/<student_id>/next`
**Description**: Get the next diagnostic test question

**Response:**
```json
{
  "status": "question",
  "question_number": 1,
  "total_questions": 22,
  "question": {
    "question_id": "q_001",
    "topic_id": "operacoes_basicas",
    "topic_name": "Operações Básicas",
    "problem": "Quanto é 15 + 23?",
    "answer": "38",
    "difficulty": "easy"
  }
}
```

**When test is complete:**
```json
{
  "status": "test_completed",
  "diagnostic_results": {
    "overall_accuracy": 0.68,
    "total_questions": 22,
    "total_correct": 15,
    "recommended_path": {
      "path_id": "intermediate",
      "path_title": "Intermediário",
      "starting_topic": "variaveis_expressoes",
      "reason": "Você domina operações básicas..."
    },
    "mastered_topics": ["operacoes_basicas", "numeros_inteiros"],
    "next_topics": [...]
  }
}
```

**Example:**
```bash
curl http://localhost:5000/diagnostic/aluno_001/next
```

---

### `POST /diagnostic/<student_id>/submit`
**Description**: Submit answer to diagnostic question

**Request:**
```json
{
  "question_id": "q_001",
  "answer": "38"
}
```

**Response:**
```json
{
  "is_correct": true,
  "correct_answer": "38",
  "status": "continue"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/diagnostic/aluno_001/submit \
  -H "Content-Type: application/json" \
  -d '{"question_id": "q_001", "answer": "38"}'
```

---

## 🎯 Adaptive Learning Endpoints

### `POST /adaptive/start`
**Description**: Start an adaptive learning session (requires completed diagnostic test)

**Request:**
```json
{
  "student_id": "student_123",
  "learning_path": "intermediate"  // Optional: "beginner", "intermediate", "advanced"
}
```

**Response:**
```json
{
  "student_id": "student_123",
  "message": "Adaptive session started",
  "current_topic": "variaveis_expressoes",
  "topic_name": "Variáveis e Expressões",
  "topic_description": "Entender variáveis e expressões algébricas",
  "difficulty": "medium"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/adaptive/start \
  -H "Content-Type: application/json" \
  -d '{"student_id": "aluno_001"}'
```

---

### `GET /adaptive/<student_id>/next`
**Description**: Get next adaptive question based on student's current level

**Response:**
```json
{
  "id": "q_adaptive_001",
  "topic": "Variáveis e Expressões",
  "topic_id": "variaveis_expressoes",
  "difficulty": "medium",
  "problem": "Se x = 5, quanto é 3x + 7?",
  "answer": "22",
  "type": "variables_expressions",
  "steps": [
    "Substitua x por 5: 3(5) + 7",
    "Multiplique: 15 + 7",
    "Some: 22"
  ],
  "concepts": ["substituição", "ordem_operacoes"]
}
```

**Example:**
```bash
curl http://localhost:5000/adaptive/aluno_001/next
```

---

### `POST /adaptive/<student_id>/submit`
**Description**: Submit answer to adaptive question and get feedback

**Request:**
```json
{
  "question_id": "q_adaptive_001",
  "question": "Se x = 5, quanto é 3x + 7?",
  "student_answer": "22",
  "correct_answer": "22",
  "solution_steps": ["Substitua x por 5...", "..."],
  "concepts_tested": ["substituição", "ordem_operacoes"]
}
```

**Response (Correct):**
```json
{
  "is_correct": true,
  "status": "continue",
  "message": "Correto! Continue praticando.",
  "performance": {
    "consecutive_correct": 3,
    "topic_accuracy": 0.85
  }
}
```

**Response (Topic Mastered):**
```json
{
  "is_correct": true,
  "status": "topic_mastered",
  "message": "Parabéns! Você dominou 'Variáveis e Expressões'!",
  "new_topic_id": "simplificacao_algebrica",
  "new_topic_name": "Simplificação Algébrica"
}
```

**Response (Prerequisite Gap Detected):**
```json
{
  "is_correct": false,
  "status": "prerequisite_required",
  "message": "Vamos revisar um tópico anterior",
  "prerequisite_topic_id": "operacoes_basicas",
  "new_topic_name": "Operações Básicas",
  "reason": "Detected gap in: adição, subtração",
  "hint": "Revise operações básicas antes de continuar"
}
```

**Response (Difficulty Reduced):**
```json
{
  "is_correct": false,
  "status": "difficulty_reduced",
  "message": "Vamos tentar questões mais fáceis",
  "hint": "A resposta correta é 22. Você precisa substituir...",
  "solution_steps": ["..."]
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/adaptive/aluno_001/submit \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "q_001",
    "question": "Se x = 5, quanto é 3x + 7?",
    "student_answer": "22",
    "correct_answer": "22",
    "solution_steps": ["..."],
    "concepts_tested": ["substituição"]
  }'
```

---

### `POST /adaptive/<student_id>/hint`
**Description**: Get progressive hints for current question (3 levels)

**Request:**
```json
{
  "question": {
    "type": "one_step",
    "equation": "x + 5 = 12",
    "answer": "7"
  },
  "hint_level": 1  // 1 (gentle), 2 (specific), or 3 (directive)
}
```

**Response (Level 1 - Gentle):**
```json
{
  "hint": "Pense: qual operação está sendo feita com x?",
  "level": 1,
  "level_name": "Dica Suave",
  "max_level": 3
}
```

**Response (Level 2 - Specific):**
```json
{
  "hint": "Se tem x + 5, você deve subtrair 5 dos dois lados.",
  "level": 2,
  "level_name": "Dica Específica",
  "max_level": 3
}
```

**Response (Level 3 - Directive):**
```json
{
  "hint": "Faça: x + 5 - 5 = 12 - 5. Isso dará x = 7.",
  "level": 3,
  "level_name": "Dica Diretiva",
  "max_level": 3
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/adaptive/aluno_001/hint \
  -H "Content-Type: application/json" \
  -d '{
    "question": {"type": "one_step", "equation": "x + 5 = 12", "answer": "7"},
    "hint_level": 1
  }'
```

---

## 📊 Progress Tracking Endpoints

### `GET /progress/<student_id>`
**Description**: Get comprehensive student progress report

**Response:**
```json
{
  "student_id": "student_123",
  "total_topics": 11,
  "mastered_count": 3,
  "completion_percentage": 27.3,
  "current_topic": "Equações Lineares - 1 Etapa",
  "progress_by_topic": {
    "operacoes_basicas": {
      "name": "Operações Básicas",
      "is_mastered": true,
      "accuracy_rate": 0.95,
      "questions_answered": 20,
      "mastered_on": "2025-01-08"
    },
    "variaveis_expressoes": {
      "name": "Variáveis e Expressões",
      "is_mastered": false,
      "accuracy_rate": 0.72,
      "questions_answered": 15,
      "recent_performance": 0.80
    }
  }
}
```

**Example:**
```bash
curl http://localhost:5000/progress/aluno_001
```

---

### `GET /progress/<student_id>/recommendations`
**Description**: Get personalized topic recommendations

**Response:**
```json
{
  "student_id": "student_123",
  "recommendations": [
    {
      "topic_id": "equacoes_lineares_uma_etapa",
      "name": "Equações Lineares - 1 Etapa",
      "description": "Resolver equações de uma etapa",
      "difficulty": 2,
      "why_recommended": "Prerequisites mastered",
      "estimated_questions": 15,
      "prerequisites_met": true
    },
    {
      "topic_id": "simplificacao_algebrica",
      "name": "Simplificação Algébrica",
      "description": "Combinar termos semelhantes...",
      "difficulty": 2,
      "why_recommended": "Natural progression",
      "estimated_questions": 12,
      "prerequisites_met": true
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:5000/progress/aluno_001/recommendations
```

---

## 📚 Topic and Knowledge Graph Endpoints

### `GET /topics/available`
**Description**: Get all available math topics with metadata

**Response:**
```json
{
  "topics": [
    {
      "topic_id": "operacoes_basicas",
      "name": "Operações Básicas",
      "description": "Adição, subtração, multiplicação e divisão",
      "difficulty": 1,
      "prerequisites": [],
      "has_questions": true
    },
    {
      "topic_id": "equacoes_lineares_uma_etapa",
      "name": "Equações Lineares - 1 Etapa",
      "description": "Resolver equações de uma etapa",
      "difficulty": 2,
      "prerequisites": ["operacoes_inversas", "manipulacao_equacoes"],
      "has_questions": true
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:5000/topics/available
```

---

## 💬 Socratic Teaching Endpoints

### `POST /start`
**Description**: Start a Socratic teaching session for a specific problem

**Request:**
```json
{
  "problem": "Solve for x: 2x + 5 = 13"
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "problem": "Solve for x: 2x + 5 = 13",
  "question": "O que esta equação está pedindo para você encontrar?",
  "phase": "UNDERSTANDING",
  "hint_level": 0,
  "created_at": "2025-01-08T12:00:00"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/start \
  -H "Content-Type: application/json" \
  -d '{"problem": "Solve for x: 2x + 5 = 13"}'
```

---

### `POST /respond`
**Description**: Submit student response in Socratic session

**Request:**
```json
{
  "session_id": "uuid-string",
  "response": "Encontrar o valor de x"
}
```

**Response:**
```json
{
  "question": "Ótimo! Que informações a equação te dá?",
  "phase": "UNDERSTANDING",
  "hint_level": 0,
  "is_complete": false,
  "encouragement": "Você está pensando bem!"
}
```

**When complete:**
```json
{
  "question": "Parabéns! Você resolveu corretamente.",
  "phase": "REVIEW",
  "hint_level": 0,
  "is_complete": true,
  "message": "Session completed successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/respond \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc-123", "response": "Encontrar x"}'
```

---

### `GET /session/<id>`
**Description**: Get session details and conversation history

**Response:**
```json
{
  "session_id": "uuid-string",
  "problem": "Solve for x: 2x + 5 = 13",
  "current_phase": "PLANNING",
  "hint_level": 1,
  "is_complete": false,
  "conversation": [
    {
      "role": "teacher",
      "content": "O que esta equação está pedindo?",
      "phase": "UNDERSTANDING",
      "hint_level": 0,
      "timestamp": "2025-01-08T12:00:00"
    },
    {
      "role": "student",
      "content": "Encontrar x",
      "timestamp": "2025-01-08T12:01:00"
    }
  ],
  "created_at": "2025-01-08T12:00:00",
  "updated_at": "2025-01-08T12:01:00"
}
```

**Example:**
```bash
curl http://localhost:5000/session/abc-123
```

---

### `DELETE /session/<id>`
**Description**: End and delete a Socratic teaching session

**Response:**
```json
{
  "message": "Session deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:5000/session/abc-123
```

---

### `GET /sessions`
**Description**: List all active Socratic teaching sessions

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "uuid-string",
      "problem": "Solve for x: 2x + 5 = 13",
      "current_phase": "EXECUTION",
      "is_complete": false,
      "created_at": "2025-01-08T12:00:00",
      "num_exchanges": 5
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:5000/sessions
```

---

## 📝 Practice Question Endpoints

### `POST /questions/generate`
**Description**: Generate practice questions for specific topic

**Request:**
```json
{
  "topic": "linear_equations",
  "difficulty": "medium",
  "count": 5
}
```

**Response:**
```json
{
  "questions": [
    {
      "id": "q_001",
      "topic": "linear_equations",
      "difficulty": "medium",
      "problem": "Solve for x: 3x - 7 = 14",
      "answer": "7",
      "steps": ["Add 7 to both sides...", "..."],
      "concepts": ["inverse_operations", "one_step_equations"]
    }
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/questions/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "linear_equations", "difficulty": "medium", "count": 5}'
```

---

## 📚 Available Math Topics

The knowledge graph contains 11 interconnected topics:

1. **Operações Básicas** (Level 1) - Addition, subtraction, multiplication, division
2. **Números Inteiros** (Level 1) - Working with positive and negative numbers
3. **Frações** (Level 2) - Operations with fractions and decimals
4. **Variáveis e Expressões** (Level 2) - Understanding variables and expressions
5. **Simplificação Algébrica** (Level 2) - Combining like terms
6. **Operações Inversas** (Level 2) - Additive and multiplicative inverses
7. **Manipulação de Equações** (Level 2) - Equation manipulation fundamentals
8. **Equações Lineares - 1 Etapa** (Level 2) - One-step linear equations
9. **Equações Lineares - 2 Etapas** (Level 3) - Two-step linear equations
10. **Equações Lineares - Variáveis Ambos Lados** (Level 4) - Variables on both sides
11. **Equações Lineares Geral** (Level 4) - General linear equations

**Learning Paths:**
- **Beginner**: Starts at Operações Básicas (9 topics)
- **Intermediate**: Starts at Variáveis e Expressões (7 topics)
- **Advanced**: Starts at Equações Lineares - 1 Etapa (4 topics)

## How It Works

### 1. Polya's 4 Phases

**Phase 1: Understanding the Problem**
- Goals: Identify unknowns, given information, constraints
- Example questions:
  - "What is this equation asking you to find?"
  - "What information does the problem give you?"

**Phase 2: Devising a Plan**
- Goals: Choose strategy, identify operations needed
- Example questions:
  - "What strategy could you use to isolate x?"
  - "Have you solved similar problems before?"

**Phase 3: Carrying Out the Plan**
- Goals: Execute steps carefully, check as you go
- Example questions:
  - "What do you get when you subtract 5 from both sides?"
  - "Can you show me the next step?"

**Phase 4: Looking Back (Review)**
- Goals: Verify solution, reflect on process
- Example questions:
  - "How can you check if your answer is correct?"
  - "What happens if you substitute x=4 back into the equation?"

### 2. Adaptive Learning System

**Diagnostic Phase:**
- Tests student across all 11 topics (2 questions per topic)
- Calculates accuracy per topic
- Identifies mastered topics
- Recommends learning path (Beginner/Intermediate/Advanced)

**Adaptive Practice:**
- Starts at recommended topic based on diagnostic
- Automatically adjusts difficulty based on performance:
  - 3+ consecutive correct → increase difficulty
  - 2+ consecutive incorrect → decrease difficulty
  - Conceptual errors → return to prerequisite topics
- Mastery detection: ≥80% accuracy + no repeated conceptual errors
- Automatic progression to next topic when current is mastered

**Error Analysis:**
- AI-powered error classification:
  - **CONCEPTUAL**: Fundamental misunderstanding of concept
  - **PROCEDURAL**: Knows concept but wrong steps
  - **ARITHMETIC**: Calculation errors
  - **CARELESS**: Simple mistakes
- Identifies affected concepts and missing prerequisites
- Recommends specific remediation

### 3. Progressive Hint System

**3-Level Escalation:**
- **Level 1 (Gentle)**: Open-ended questions - "Pense: qual operação está sendo feita com x?"
- **Level 2 (Specific)**: Pointed hints - "Se tem x + 5, você deve subtrair 5 dos dois lados"
- **Level 3 (Directive)**: Step-by-step guidance - "Faça: x + 5 - 5 = 12 - 5. Isso dará x = 7"

Students can request hints at any time via the `/adaptive/<student_id>/hint` endpoint.

### 4. AI Tutor Commentary

Provides contextual feedback in Portuguese:
- **Greetings**: Welcome messages for new questions
- **Correct Answers**: Positive reinforcement and encouragement
- **Incorrect Answers**: Specific feedback based on error type
- **Encouragement**: Streak-based motivation (3, 5, 10 correct in a row)
- **Topic Mastery**: Celebration messages when topics are mastered

### 5. Session Management

- All progress stored in JSON files:
  - `student_progress.json` - Student progress and mastery data
  - `sessions/` - Socratic teaching session conversations
  - `questions.json` - Generated practice questions
- Data persists across server restarts
- No database required

## Project Structure

```
q-edu/
├── app.py                        # Flask API server (main entry point)
│
├── Core Adaptive Learning:
│   ├── adaptive_engine.py        # Main adaptive learning orchestration
│   ├── diagnostic_test.py        # Initial assessment system
│   ├── knowledge_graph_manager.py # Topic navigation & prerequisites
│   ├── mastery_tracker.py        # Student progress tracking
│   ├── error_analyzer.py         # AI-powered error classification
│   └── tutor_commentary.py       # AI tutor feedback generation
│
├── Socratic Teaching:
│   ├── socratic_solver.py        # Core Socratic teaching logic
│   ├── polya_phases.py          # Polya's 4-phase implementation
│   ├── hint_system.py           # Hint escalation system
│   └── conversation_manager.py   # Session persistence
│
├── Question Management:
│   ├── question_bank.py          # Question generators for all topics
│   ├── question_manager.py       # Question lifecycle management
│   └── generate_test_questions.py # Batch question generation
│
├── Configuration & Data:
│   ├── knowledge_graph.json      # 11-topic structure with prerequisites
│   ├── student_progress.json     # Student progress data (auto-created)
│   ├── questions.json            # Generated questions cache
│   ├── .env                      # API key (create this)
│   └── pyproject.toml           # Dependencies
│
├── Testing & Examples:
│   ├── test_adaptive_system.py   # Adaptive system tests
│   └── example_client.py         # API usage examples
│
└── Storage (auto-created):
    └── sessions/                 # Socratic session conversations
```

## Example Teaching Session

**Problem**: "Solve for x: 2x + 5 = 13"

**Conversation**:
```
Teacher: What is this equation asking you to find?
Student: The value of x

Teacher: Good! What information does the equation give you?
Student: 2x + 5 equals 13

Teacher: Excellent! Now, what strategy could you use to isolate x?
Student: I'm not sure...

Teacher [escalates hint]: What would happen if you subtracted 5 from both sides?
Student: I'd get 2x = 8

Teacher: Perfect! What's the next step?
Student: Divide both sides by 2?

Teacher: Exactly! What do you get?
Student: x = 4

Teacher: Great work! How can you verify this answer is correct?
Student: Substitute 4 back into the equation

Teacher: Go ahead and try that!
Student: 2(4) + 5 = 8 + 5 = 13. It works!

Teacher: Excellent problem-solving! You've successfully completed all phases.
```

## Development

### Running Tests
```bash
# Run the example client
uv run python example_client.py
```

### Debug Mode
The Flask server runs in debug mode by default. Set `debug=False` in `app.py` for production.

## Troubleshooting

### API Key Error
If you see "GEMINI_API_KEY not found":
1. Ensure `.env` file exists
2. Verify format: `GEMINI_API_KEY=your_key_here`
3. No spaces around `=`

### Import Errors
```bash
uv sync  # Reinstall all dependencies
```

### Session Not Found
Sessions are stored in `sessions/` directory. If deleted, the session is lost.

## Completed Features

- ✅ **Diagnostic Testing**: Initial assessment across 11 topics
- ✅ **Adaptive Learning**: Automatic difficulty adjustment and prerequisite detection
- ✅ **Knowledge Graph**: 11 interconnected math topics
- ✅ **Progress Tracking**: Mastery detection and analytics
- ✅ **Error Analysis**: AI-powered error classification
- ✅ **Progressive Hints**: 3-level hint system
- ✅ **AI Tutor Commentary**: Contextual feedback in Portuguese
- ✅ **Socratic Teaching**: Polya's method implementation
- ✅ **RESTful API**: Complete backend with Swagger docs
- ✅ **Session Persistence**: JSON-based storage

## Future Enhancements

- [ ] **Frontend**: Build web/mobile interface for student use
- [ ] **Multi-language Support**: English, Spanish, and other languages
- [ ] **Voice Interface**: Integration with speech-to-text and text-to-speech
- [ ] **More Math Domains**: Geometry, calculus, statistics, probability
- [ ] **Advanced Analytics**: Detailed learning analytics and insights
- [ ] **Export Features**: PDF reports, progress certificates
- [ ] **LMS Integration**: Integration with Canvas, Moodle, Google Classroom
- [ ] **Gamification**: Points, badges, leaderboards
- [ ] **Collaborative Learning**: Student-to-student problem solving
- [ ] **Parent/Teacher Dashboard**: Monitor multiple students

## Contributing

Contributions are welcome! Please submit issues or pull requests.

## License

[Add your license here]

## Acknowledgments

- Based on George Polya's "How to Solve It" (1945)
- Powered by Google's Gemini AI
- Inspired by Socratic teaching methodology
