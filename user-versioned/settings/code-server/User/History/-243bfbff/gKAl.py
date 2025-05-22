# Modified document_service.py
import os
import streamlit as st
from typing import List, Dict, Any, Optional
import base64
import uuid

def init_document_state():
    """Initialize document-related session state variables if they don't exist."""
    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = {}

def get_uploaded_documents() -> List[Dict[str, Any]]:
    """
    Get list of uploaded documents.
    
    Returns:
        List of document objects with name, type, and id
    """
    init_document_state()
    return list(st.session_state.uploaded_documents.values())

def process_uploaded_file(file) -> Dict[str, Any]:
    """
    Process an uploaded file and store its metadata.
    
    Args:
        file: Streamlit UploadedFile object
        
    Returns:
        Dict with document metadata
    """
    init_document_state()
    
    # Generate a unique ID for this document
    doc_id = str(uuid.uuid4())
    
    # Get file extension
    _, file_extension = os.path.splitext(file.name)
    
    # Store document metadata
    document = {
        "id": doc_id,
        "name": file.name,
        "type": file_extension.lower().replace(".", ""),
        "size": file.size,
        "uploaded_at": str(st.session_state.get("today", ""))
    }
    
    # Add to session state
    st.session_state.uploaded_documents[doc_id] = document
    
    return document

def remove_document(document_name: str) -> bool:
    """
    Remove a document from the uploaded documents list.
    
    Args:
        document_name: Name of document to remove
        
    Returns:
        Boolean indicating success/failure
    """
    init_document_state()
    
    # Find the document with the matching name
    for doc_id, doc in list(st.session_state.uploaded_documents.items()):
        if doc["name"] == document_name:
            # Remove document from session state
            del st.session_state.uploaded_documents[doc_id]
            return True
            
    return False

def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """
    Get document metadata by ID.
    
    Args:
        document_id: ID of document to retrieve
        
    Returns:
        Document metadata dict or None if not found
    """
    init_document_state()
    return st.session_state.uploaded_documents.get(document_id)