#text_extractor.py
import streamlit as st
import requests
import tempfile
import os
import tiktoken
from unstructured.partition.auto import partition
from utils.constants import DOCUMENT_QUERY_API_ENDPOINT, API_ENDPOINT

def extract_text_from_file(file):
    """Extract text from uploaded file using unstructured package."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_file_path = tmp_file.name
    try:
        elements = partition(tmp_file_path)
        text = "\n\n".join([str(e) for e in elements])
    finally:
        os.unlink(tmp_file_path)
    return text

def extract_text_from_file(file):
    ext = get_file_extension(file.name)

    if ext == 'txt':
        return file.read().decode('utf-8')
    elif ext == 'pdf':
        from PyPDF2 import PdfReader
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif ext in ['docx', 'doc']:
        from docx import Document
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return None

def truncate_text_to_token_limit(text, max_tokens=5000, encoding_name="cl100k_base"):
    """Truncate text to stay within token limit."""
    tokenizer = tiktoken.get_encoding(encoding_name)
    tokens = tokenizer.encode(text)
    if len(tokens) <= max_tokens:
        return text
    truncated = tokenizer.decode(tokens[:max_tokens])
    return truncated

def process_document(file):
    """Process an uploaded document for text extraction and querying."""
    full_text = extract_text_from_file(file)
    truncated_text = truncate_text_to_token_limit(full_text)
    tokenizer = tiktoken.get_encoding("cl100k_base")
    
    # Store the processed information in session state for later use
    if "document_cache" not in st.session_state:
        st.session_state.document_cache = {}
    
    # Cache the document data with the filename as key
    st.session_state.document_cache[file.name] = {
        "text": truncated_text,
        "original_token_count": len(tokenizer.encode(full_text)),
        "truncated_token_count": len(tokenizer.encode(truncated_text))
    }
    
    return {
        "filename": file.name,
        "original_token_count": len(tokenizer.encode(full_text)),
        "truncated_token_count": len(tokenizer.encode(truncated_text)),
        "text": truncated_text
    }

def query_document(query, document_text):
    """
    Send a query to process against document text.
    
    Args:
        query (str): User's query about the document
        document_text (str): Extracted text from the document
        
    Returns:
        dict: Response containing the answer
    """
    try:
        payload = {
            "query": query,
            "extracted_text": document_text,
            "token_threshold": 5000
        }
        response = requests.post(
            DOCUMENT_QUERY_API_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code != 200:
            raise Exception(f"API returned {response.status_code}: {response.text}")
        try:
            result = response.json()
            return {"answer": str(result.get("message", result))}
        except ValueError:
            return {"answer": response.text}
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")

def get_stored_document_text(document_name=None):
    """
    Get the stored document text from session state.
    
    Args:
        document_name (str, optional): Name of document to retrieve. If None, returns the first document.
        
    Returns:
        str or None: Document text if available, otherwise None
    """
    if "document_cache" not in st.session_state or not st.session_state.document_cache:
        return None
        
    if document_name and document_name in st.session_state.document_cache:
        return st.session_state.document_cache[document_name]["text"]
    
    # If no specific document requested, return the first one
    first_doc = next(iter(st.session_state.document_cache.values()))
    return first_doc["text"]

def handle_query(query, use_document_mode=False):
    """
    Handle user query by routing to the appropriate endpoint based on mode.
    
    Args:
        query (str): User's query
        use_document_mode (bool): Whether to query against stored document
        
    Returns:
        dict: Response containing results
    """
    if use_document_mode:
        # Check if we have a document to query against
        document_text = get_stored_document_text()
        if not document_text:
            return {"success": False, "message": "No document available. Please upload a document first."}
            
        # Query against the document
        try:
            result = query_document(query, document_text)
            return {
                "success": True,
                "message": result.get("answer", "No answer found"),
                "context": "Query processed against uploaded document."
            }
        except Exception as e:
            return {"success": False, "message": f"Error processing document query: {str(e)}"}
    else:
        # Use the regular API endpoint
        try:
            from services.api_service import generate_chat_response
            return generate_chat_response(query)
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}