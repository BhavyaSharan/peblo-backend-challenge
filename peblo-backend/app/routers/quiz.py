from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..database import get_supabase
from ..models import QuizGenerateRequest, QuestionResponse, QuizSubmitRequest, QuizSubmitResponse
from ..services.llm import generate_questions_from_chunk
import random
import json

router = APIRouter()

@router.post("/generate-quiz")
def generate_quiz(request: QuizGenerateRequest):
    """Generates quiz questions from ingested content chunks based on a topic."""
    supabase = get_supabase()
    
    # Query for chunks matching the topic
    query = supabase.table("content_chunks").select("*").eq("topic", request.topic)
    if request.grade:
        query = query.eq("grade", request.grade)
    if request.subject:
        query = query.eq("subject", request.subject)
        
    res = query.execute()
    chunks = res.data
    
    if not chunks:
        raise HTTPException(status_code=404, detail="No content chunks found for the given criteria.")
        
    # Pick a random chunk (in a real scenario, you'd aggregate or use vector search)
    selected_chunk = random.choice(chunks)
    
    # Generate questions via LLM
    try:
        new_questions = generate_questions_from_chunk(selected_chunk["text_content"], num_questions=request.num_questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")
        
    # Insert questions into Supabase
    inserts = []
    response_questions = []
    
    for q in new_questions:
        insert_data = {
            "source_chunk_id": selected_chunk["chunk_id"],
            "question_type": q.get("question_type"),
            "question_text": q.get("question"),
            "options": q.get("options"), # JSONB array
            "answer": q.get("answer"),
            "difficulty": q.get("difficulty")
        }
        
        db_res = supabase.table("questions").insert(insert_data).execute()
        
        if db_res.data:
            inserted_id = db_res.data[0]["id"]
            response_questions.append({
                "id": inserted_id,
                **insert_data
            })
            
    return {"message": "Quiz generated successfully.", "questions": response_questions}

@router.get("/quiz", response_model=List[QuestionResponse])
def get_quiz(
    topic: str,
    difficulty: Optional[str] = None,
    limit: int = 5
):
    """Fetches questions."""
    supabase = get_supabase()
    
    # Needs to join questions and content_chunks to filter by topic
    # For simplicity, we query chunks then questions, or use Supabase foreign key querying
    chunks_res = supabase.table("content_chunks").select("chunk_id").eq("topic", topic).execute()
    chunk_ids = [c["chunk_id"] for c in chunks_res.data]
    
    if not chunk_ids:
        return []
        
    query = supabase.table("questions").select("*").in_("source_chunk_id", chunk_ids)
    if difficulty:
         query = query.eq("difficulty", difficulty)
         
    questions_res = query.limit(limit).execute()
    return questions_res.data

@router.post("/submit-answer", response_model=QuizSubmitResponse)
def submit_answer(payload: QuizSubmitRequest):
    """Submits a student answer and updates adaptive difficulty."""
    supabase = get_supabase()
    
    # Fetch question to check correct answer
    q_res = supabase.table("questions").select("answer, difficulty, source_chunk_id").eq("id", str(payload.question_id)).execute()
    if not q_res.data:
        raise HTTPException(status_code=404, detail="Question not found.")
        
    question = q_res.data[0]
    is_correct = (payload.selected_answer.strip().lower() == question["answer"].strip().lower())
    
    # Record answer
    supabase.table("student_answers").insert({
        "student_id": payload.student_id,
        "question_id": str(payload.question_id),
        "selected_answer": payload.selected_answer,
        "is_correct": is_correct
    }).execute()
    
    # Update adaptive difficulty progress
    diff_levels = ["easy", "medium", "hard"]
    
    # Get topic from chunk
    chunk_res = supabase.table("content_chunks").select("topic").eq("chunk_id", question["source_chunk_id"]).execute()
    topic = chunk_res.data[0]["topic"] if chunk_res.data else "General"
    
    # Upsert progress
    prog_res = supabase.table("student_progress").select("*").eq("student_id", payload.student_id).eq("topic", topic).execute()
    
    if prog_res.data:
        prog = prog_res.data[0]
        curr_diff = prog["current_difficulty"]
        
        # Adaptive logic:
        # Correct -> If 2 correct in a row at this diff, bump up
        # Incorrect -> Immediately bump down
        
        new_diff = curr_diff
        curr_idx = diff_levels.index(curr_diff)
        
        if is_correct:
            if prog["correct_count"] >= 1 and curr_idx < len(diff_levels) - 1:
                new_diff = diff_levels[curr_idx + 1]
                supabase.table("student_progress").update({"current_difficulty": new_diff, "correct_count": 0, "incorrect_count": 0}).eq("id", prog["id"]).execute()
            else:
                 supabase.table("student_progress").update({"correct_count": prog["correct_count"] + 1, "incorrect_count": 0}).eq("id", prog["id"]).execute()
        else:
             if curr_idx > 0:
                 new_diff = diff_levels[curr_idx - 1]
                 supabase.table("student_progress").update({"current_difficulty": new_diff, "incorrect_count": prog["incorrect_count"] + 1, "correct_count": 0}).eq("id", prog["id"]).execute()
             else:
                 supabase.table("student_progress").update({"incorrect_count": prog["incorrect_count"] + 1, "correct_count": 0}).eq("id", prog["id"]).execute()
                 
    else:
        # First time answering for this topic
        new_diff = "easy"
        supabase.table("student_progress").insert({
            "student_id": payload.student_id,
            "topic": topic,
            "current_difficulty": new_diff,
            "correct_count": 1 if is_correct else 0,
            "incorrect_count": 1 if not is_correct else 0
        }).execute()

    return QuizSubmitResponse(
        is_correct=is_correct,
        correct_answer=question["answer"],
        current_difficulty=new_diff,
        message="Answer correct! Difficulty increased." if is_correct and new_diff != question["difficulty"] else ("Answer correct." if is_correct else "Answer incorrect. Difficulty decreased.")
    )
