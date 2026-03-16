-- Run this script in the Supabase SQL Editor to create the required tables

-- 1. Documents Table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id VARCHAR NOT NULL UNIQUE,
    filename VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Content Chunks Table
CREATE TABLE content_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chunk_id VARCHAR NOT NULL UNIQUE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    grade INTEGER,
    subject VARCHAR,
    topic VARCHAR,
    text_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Questions Table
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_chunk_id VARCHAR REFERENCES content_chunks(chunk_id) ON DELETE CASCADE,
    question_type VARCHAR NOT NULL, -- e.g., 'MCQ', 'True/False', 'Fill in the blank'
    question_text TEXT NOT NULL,
    options JSONB, -- Array of strings for MCQ, or null for others
    answer TEXT NOT NULL,
    difficulty VARCHAR NOT NULL, -- 'easy', 'medium', 'hard'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Student Progress Table (to track moving difficulty)
CREATE TABLE student_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id VARCHAR NOT NULL,
    topic VARCHAR NOT NULL,
    current_difficulty VARCHAR DEFAULT 'easy',
    correct_count INTEGER DEFAULT 0,
    incorrect_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id, topic)
);

-- 5. Student Answers Table
CREATE TABLE student_answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id VARCHAR NOT NULL,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    selected_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
