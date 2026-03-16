from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from uuid import UUID

class IngestResponse(BaseModel):
    message: str
    document_id: UUID
    chunks_count: int

class QuizGenerateRequest(BaseModel):
    topic: str
    grade: Optional[int] = None
    subject: Optional[str] = None
    num_questions: int = 5

class QuestionOptions(BaseModel):
    options: List[str]

class QuestionResponse(BaseModel):
    id: UUID
    source_chunk_id: str
    question_type: str
    question_text: str
    options: Optional[List[str]] = None
    answer: str
    difficulty: str

class QuizSubmitRequest(BaseModel):
    student_id: str
    question_id: UUID
    selected_answer: str

class QuizSubmitResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    current_difficulty: str
    message: str
