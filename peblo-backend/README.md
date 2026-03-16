# Peblo AI Backend Challenge

This is a prototype backend system built for the Peblo Backend Engineer Challenge. It ingests educational content from PDFs, stores structured data, uses Google's Gemini LLM to generate quiz questions, and serves them via an API with adaptive difficulty handling.

## Stack
- **Framework:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **LLM:** Google Gemini (`gemini-2.5-flash`)
- **PDF Extraction:** PyPDF (`pypdf`)

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- A Supabase Project
- A Google Gemini API Key

### 2. Database Setup
1. Create a new project in [Supabase](https://supabase.com/).
2. Open the SQL Editor in your Supabase dashboard.
3. Copy the contents of `schema.sql` (found in the root of this repository) and run it to create the required tables.

### 3. Local Installation

```bash
# Clone the repository (if applicable) or navigate to the directory
cd peblo-backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configuration
Create a `.env` file in the root directory (you can copy `.env.example`) and fill in your credentials:

```
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_service_role_key_here
```

### 5. Running the API
Start the FastAPI server using Uvicorn:

# If the virtual environment is activated:
uvicorn app.main:app --reload

# Or, if you are having issues with 'uvicorn is not recognized' or getting ModuleNotFoundError on Windows, use the direct module execution path:
venv\Scripts\python -m uvicorn app.main:app --reload
The API will be running at `http://localhost:8000`.

## Testing the Endpoints
You can interactively test all endpoints using the built-in Swagger UI provided by FastAPI at:
`http://localhost:8000/docs`

### 1. Ingest a PDF `POST /api/ingest`
- Upload one of the provided PDFs.
- Optionally provide `grade`, `subject`, and `topic` (e.g., topic="Shapes").

### 2. Generate Quiz `POST /api/generate-quiz`
- After ingestion, tell the LLM to generate questions for that topic.
- Example payload:
```json
{
  "topic": "Shapes",
  "num_questions": 5
}
```

### 3. Get Quiz `GET /api/quiz`
- Retrieve the generated questions.
- Example query: `?topic=Shapes&difficulty=easy`

### 4. Submit Answer `POST /api/submit-answer`
- Simulates a student answering a question.
- The system will respond indicating if it was correct and if the difficulty level adapted.
- Example payload:
```json
{
  "student_id": "S001",
  "question_id": "uuid-of-a-question",
  "selected_answer": "3"
}
```

## Architecture Notes
- The ingestion process uses basic character-level chunking with overlap. For a production system, structural or semantic chunking would be preferred.
- Adaptive difficulty currently bumps up on a correct answer and bumps down on an incorrect answer instantly for demonstration purposes. This tracks purely per topic, per student.
- Pydantic and FastAPI are used to enforce strong typing and structure out of the box, with built-in validation for the Gemini Structured Outputs.
