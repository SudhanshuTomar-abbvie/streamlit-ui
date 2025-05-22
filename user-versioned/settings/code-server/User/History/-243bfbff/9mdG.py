#document_service.py
import streamlit as st
import os
import tempfile
import logging
import uuid
import json
import base64
from typing import List, Dict, Any, Optional
import mimetypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_uploaded_file(uploaded_file):
    """
    Process an uploaded file and add it to the session state
    
    Args:
        uploaded_file: StreamlitUploadedFile object
        
    Returns:
        Dictionary with document information
    """
    try:
        # Generate a unique ID for this document
        doc_id = str(uuid.uuid4())
        
        # Get file details
        file_name = uploaded_file.name
        file_type = uploaded_file.type
        file_size = uploaded_file.size
        
        # Create temporary file to store the content
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            temp_path = tmp_file.name
        
        # Read file content for API
        with open(temp_path, "rb") as f:
            encoded_content = base64.b64encode(f.read()).decode("utf-8")
        
        # Create document info
        document_info = {
            "id": doc_id,
            "name": file_name,
            "type": file_type,
            "size": file_size,
            "temp_path": temp_path,
            "content": encoded_content  # Base64 encoded content for API
        }
        
        # Add to session state if not already there
        if "uploaded_documents" not in st.session_state:
            st.session_state.uploaded_documents = []
        
        st.session_state.uploaded_documents.append(document_info)
        
        return document_info
    
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        return None

def remove_document(doc_id):
    """
    Remove a document from the session state
    
    Args:
        doc_id: ID of the document to remove
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        for i, doc in enumerate(st.session_state.uploaded_documents):
            if doc["id"] == doc_id:
                # Delete the temporary file
                if os.path.exists(doc["temp_path"]):
                    os.unlink(doc["temp_path"])
                
                # Remove from session state
                st.session_state.uploaded_documents.pop(i)
                return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error removing document: {str(e)}")
        return False

def get_document_by_id(doc_id):
    """
    Get a document by its ID
    
    Args:
        doc_id: ID of the document to retrieve
        
    Returns:
        Document info dictionary or None if not found
    """
    for doc in st.session_state.uploaded_documents:
        if doc["id"] == doc_id:
            return doc
    
    return None

def get_uploaded_documents():
    """
    Get all uploaded documents
    
    Returns:
        List of document info dictionaries
    """
    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = []
    
    return st.session_state.uploaded_documents

def clear_all_documents():
    """
    Remove all uploaded documents
    
    Returns:
        Number of documents cleared
    """
    count = 0
    
    if "uploaded_documents" in st.session_state:
        # Delete all temporary files
        for doc in st.session_state.uploaded_documents:
            if os.path.exists(doc["temp_path"]):
                os.unlink(doc["temp_path"])
            count += 1
        
        # Clear the session state
        st.session_state.uploaded_documents = []
    
    return count

def get_api_document_format():
    """
    Format uploaded documents for the API
    
    Returns:
        List of document dictionaries in API format
    """
    api_docs = []
    
    for doc in get_uploaded_documents():
        api_docs.append({
            "file_name": doc["name"],
            "file_type": doc["type"],
            "content": doc["content"]  # Base64 encoded content
        })
    
    return api_docs

def remove_document(filename):
    """
    Remove a document from the uploaded documents list
    
    Args:
        filename: Name of the file to remove
    
    Returns:
        bool: True if document was removed, False otherwise
    """
    if "uploaded_documents" not in st.session_state:
        return False
    
    # Find the document with the matching filename
    for i, doc in enumerate(st.session_state.uploaded_documents):
        if doc.get("name") == filename:
            # Remove the document
            st.session_state.uploaded_documents.pop(i)
            return True
            
    return False