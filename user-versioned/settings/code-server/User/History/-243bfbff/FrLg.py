import requests
import logging
import streamlit as st
from utils.constants import DOCUMENT_QUERY_API_ENDPOINT

def process_document_query(document_files, user_query):
    """
    Process documents with a user query via the backend API
    
    Args:
        document_files (list): List of uploaded file objects
        user_query (str): User's query about the documents
        
    Returns:
        dict: Response with text and context
    """
    try:
        # Prepare files for multipart/form-data upload
        files = {}
        for i, file in enumerate(document_files):
            files[f'document_{i}'] = (file.name, file.getvalue(), f'application/{file.type.split("/")[1]}')
        
        # Prepare the payload with user query
        data = {
            "user_query": user_query
        }
        
        logging.debug(f"Sending document query request with {len(files)} files")
        
        # Make API call with both files and data
        response = requests.post(
            DOCUMENT_PROCESS_API_ENDPOINT,
            files=files,
            data=data
        )
        response.raise_for_status()
        result = response.json()
        
        logging.debug(f"Document processing response: {result}")
        
        # Extract response text and context from result
        if isinstance(result.get("response"), dict):
            response_text = result["response"].get("response", "No response available")
            context = result["response"].get("contexts", ["No context available"])
        else:
            response_text = result.get("response", "No response available")
            context = result.get("contexts", ["No context available"])
        
        return {
            "response": response_text,
            "context": context
        }
    except Exception as e:
        error_msg = f"Error processing document query: {str(e)}"
        logging.error(error_msg)
        return {
            "response": f"Sorry, I encountered an error processing your documents: {str(e)}",
            "context": []
        }