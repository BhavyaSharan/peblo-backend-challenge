from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import json
from typing import List, Optional
from ..config import settings

# Initialize Gemini Client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

class GeneratedQuestion(BaseModel):
    question_type: str = Field(description="Must be one of: 'MCQ', 'True/False', 'Fill in the blank'")
    question: str = Field(description="The question text itself")
    options: Optional[List[str]] = Field(description="List of options for MCQ. Provide exactly 4 options. Leave empty or null for True/False or Fill in the blank.")
    answer: str = Field(description="The correct answer to the question. Must exactly match one of the options if MCQ.")
    difficulty: str = Field(description="Must be one of: 'easy', 'medium', 'hard'")

class QuizGenerationResult(BaseModel):
    questions: List[GeneratedQuestion]

def generate_questions_from_chunk(chunk_text: str, num_questions: int = 3) -> List[dict]:
    """
    Given a chunk of text, asks the LLM to generate educational quiz questions.
    Returns a list of dicts.
    """
    
    prompt = f"""
    You are an expert AI teacher designed to create high-quality educational assessments.
    Read the following text content carefully, and generate exactly {num_questions} quiz questions based on the information provided.
    
    Ensure a mix of 'MCQ' (Multiple Choice), 'True/False', and 'Fill in the blank' questions if possible, 
    and assign a reasonable difficulty ('easy', 'medium', 'hard') to each.
    
    Content:
    ---
    {chunk_text}
    ---
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=QuizGenerationResult,
        ),
    )
    
    try:
        # Load the raw string into dict
        result_dict = json.loads(response.text)
        return result_dict.get("questions", [])
    except Exception as e:
        print(f"Failed to parse LLM response: {e}")
        return []
