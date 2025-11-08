# Q-Edu: Socratic Math Teacher

An AI-powered Socratic teaching system that guides students through mathematical problem-solving using **Polya's Method** and **adaptive hint escalation**. Instead of giving direct answers, Q-Edu asks thought-provoking questions to help students discover solutions themselves.

## Features

- **Polya's 4-Phase Method**: Guides students through Understanding → Planning → Execution → Review
- **Socratic Questioning**: Never gives direct answers; asks probing questions instead
- **Adaptive Hint Escalation**: Detects when students struggle and provides more directive guidance
  - Level 0 (Gentle): Open-ended questions
  - Level 1 (Specific): Pointed questions with context
  - Level 2 (Directive): Step-by-step guidance
- **Session Persistence**: Conversation history saved to files, can resume later
- **RESTful API**: Easy integration with web apps, chatbots, or educational platforms

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

### `POST /start`
Start a new teaching session

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
  "question": "What is this equation asking you to find?",
  "phase": "UNDERSTANDING",
  "hint_level": 0,
  "created_at": "2025-01-08T12:00:00"
}
```

### `POST /respond`
Submit student response and get next question

**Request:**
```json
{
  "session_id": "uuid-string",
  "response": "It's asking me to find x"
}
```

**Response:**
```json
{
  "question": "Good! What information does the equation give you?",
  "phase": "UNDERSTANDING",
  "hint_level": 0,
  "is_complete": false
}
```

### `GET /session/<id>`
Retrieve session details and conversation history

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
      "content": "What is this equation asking you to find?",
      "phase": "UNDERSTANDING",
      "hint_level": 0,
      "timestamp": "..."
    },
    {
      "role": "student",
      "content": "Find x",
      "timestamp": "..."
    }
  ],
  "created_at": "...",
  "updated_at": "..."
}
```

### `DELETE /session/<id>`
End and delete a teaching session

**Response:**
```json
{
  "message": "Session deleted successfully"
}
```

### `GET /sessions`
List all teaching sessions

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "uuid-string",
      "problem": "Solve for x: 2x + 5 = 13",
      "current_phase": "EXECUTION",
      "is_complete": false,
      "created_at": "...",
      "num_exchanges": 5
    }
  ]
}
```

## Using curl

### Start a session:
```bash
curl -X POST http://localhost:5000/start \
  -H "Content-Type: application/json" \
  -d '{"problem": "Solve for x: 2x + 5 = 13"}'
```

### Submit response:
```bash
curl -X POST http://localhost:5000/respond \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "response": "We need to find x"
  }'
```

### Get session details:
```bash
curl http://localhost:5000/session/your-session-id
```

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

### 2. Adaptive Hint Escalation

The system detects struggle through:
- Explicit indicators: "I don't know", "I'm stuck"
- Vague responses: Very short answers, "umm", "maybe"
- No progress after multiple exchanges

**Level 0 (Gentle)**: "What do you notice about this equation?"
**Level 1 (Specific)**: "What would happen if you subtracted 5 from both sides?"
**Level 2 (Directive)**: "Subtract 5 from both sides. What do you get?"

### 3. Session Management

- Sessions stored as JSON files in `sessions/` directory
- Each session tracks:
  - Full conversation history
  - Current Polya phase
  - Hint escalation level
  - Struggle detection metrics
- Sessions persist across server restarts

## Project Structure

```
q-edu/
├── app.py                     # Flask API server
├── socratic_solver.py         # Core Socratic teaching logic
├── polya_phases.py           # Polya's method implementation
├── hint_system.py            # 3-level hint escalation
├── conversation_manager.py   # Session persistence
├── example_client.py         # Example usage script
├── sessions/                 # Session storage (auto-created)
├── .env                      # API key (create this)
├── .gitignore               # Git ignore rules
├── pyproject.toml           # Dependencies
└── README.md                # This file
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

## Future Enhancements

- [ ] Multi-language support
- [ ] Voice interface integration
- [ ] More math domains (geometry, calculus, statistics)
- [ ] Student progress tracking and analytics
- [ ] Export conversation as PDF for review
- [ ] Integration with learning management systems (LMS)

## Contributing

Contributions are welcome! Please submit issues or pull requests.

## License

[Add your license here]

## Acknowledgments

- Based on George Polya's "How to Solve It" (1945)
- Powered by Google's Gemini AI
- Inspired by Socratic teaching methodology
