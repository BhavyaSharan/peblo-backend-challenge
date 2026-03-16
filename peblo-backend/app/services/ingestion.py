import re
from typing import List
from pypdf import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a given PDF file path."""
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        raise e
    return text

def clean_text(text: str) -> str:
    """Cleans up the extracted text."""
    # Remove multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    # Basic unicode replacement or other cleanup if necessary
    return text.strip()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Breaks text into chunks.
    For this basic prototype, we use a simple character-based chunking with overlap.
    In a real app, sentence-based or semantic chunking (e.g. LangChain) is better.
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # If we are not at the end, try to find a natural break point (like a period or space)
        if end < text_length:
            # backtrack to the nearest space or punctuation
            while end > start and text[end] not in ['.', ' ', '\n']:
                end -= 1
            if end == start: # fallback if no space found
                end = start + chunk_size
                
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        start = end - overlap # Move start forward, leaving some overlap

    return chunks
