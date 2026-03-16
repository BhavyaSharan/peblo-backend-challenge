from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from uuid import uuid4
import os
import tempfile
from ..services.ingestion import extract_text_from_pdf, clean_text, chunk_text
from ..database import get_supabase
from ..models import IngestResponse

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    grade: Optional[int] = Form(None),
    subject: Optional[str] = Form(None),
    topic: Optional[str] = Form(None),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    supabase = get_supabase()
    
    # Save file temporarily to extract text
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
            
        # Extract and clean
        raw_text = extract_text_from_pdf(tmp_path)
        clean_ext_text = clean_text(raw_text)
        
        if not clean_ext_text:
             raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")
             
        # Chunk text
        chunks = chunk_text(clean_ext_text)
        
        # Insert Document into Supabase
        source_id = f"SRC_{uuid4().hex[:8].upper()}"
        doc_res = supabase.table("documents").insert({
            "source_id": source_id,
            "filename": file.filename
        }).execute()
        
        if not doc_res.data:
            raise HTTPException(status_code=500, detail="Failed to insert document.")
            
        doc_id = doc_res.data[0]["id"]
        
        # Insert Chunks into Supabase
        chunk_inserts = []
        for i, text_chunk in enumerate(chunks):
            chunk_id = f"{source_id}_CH_{i+1:03d}"
            chunk_inserts.append({
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "grade": grade,
                "subject": subject,
                "topic": topic,
                "text_content": text_chunk
            })
            
        if chunk_inserts:
            supabase.table("content_chunks").insert(chunk_inserts).execute()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
            
    return IngestResponse(
        message="Document ingested and chunked logically successfully.",
        document_id=doc_id,
        chunks_count=len(chunks)
    )
