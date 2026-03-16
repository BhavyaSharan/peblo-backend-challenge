# Example Sample Outputs

## 1. Extracted Content Chunk (Supabase `content_chunks` table)
```json
{
  "id": "e4b2d381-80fc-40fa-8086-a36a9b493e83",
  "chunk_id": "SRC_7E4D9A01_CH_001",
  "document_id": "c9e2b170-4f8a-4c28-98e3-512c141708a2",
  "grade": 1,
  "subject": "Math",
  "topic": "Shapes",
  "text_content": "A triangle is a shape with three straight sides and three angles. It is a polygon..."
}
```

## 2. Generated Quiz Question (Supabase `questions` table)
```json
{
  "id": "b3e215a4-9da2-48f8-a006-2581691a5db4",
  "source_chunk_id": "SRC_7E4D9A01_CH_001",
  "question_type": "MCQ",
  "question_text": "How many straight sides does a triangle have?",
  "options": ["2", "3", "4", "5"],
  "answer": "3",
  "difficulty": "easy"
}
```

## 3. Submit Answer API Response
Payload:
```json
{
  "student_id": "S001",
  "question_id": "b3e215a4-9da2-48f8-a006-2581691a5db4",
  "selected_answer": "3"
}
```

Response:
```json
{
  "is_correct": true,
  "correct_answer": "3",
  "current_difficulty": "medium",
  "message": "Answer correct! Difficulty increased."
}
```
