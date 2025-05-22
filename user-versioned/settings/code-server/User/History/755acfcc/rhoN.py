import requests
import json
import streamlit as st
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_api_request(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make a generic API request to the specified endpoint with the given payload
    
    Args:
        endpoint: API endpoint URL
        payload: JSON payload to send
        
    Returns:
        API response as dictionary or error message
    """
    try:
        logger.info(f"Making API request to {endpoint}")
        logger.debug(f"Request payload: {payload}")
        
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()  # Raise exception for HTTP errors
        
        response_data = response.json()
        logger.debug(f"Response: {response_data}")
        
        return response_data
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {str(e)}")
        return {"error": str(e), "success": False}
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return {"error": "Invalid JSON response", "success": False}
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": "An unexpected error occurred", "success": False}

def generate_chat_response(query: str, conversation_history: Optional[List] = None) -> Dict[str, Any]:
    """
    Generate a response for a chat query using the chat API
    
    Args:
        query: User's query message
        conversation_history: Optional list of previous messages
        
    Returns:
        API response containing the assistant's reply
    """
    from utils.constants import API_ENDPOINT
    
    # Prepare conversation history in the format expected by the API
    history = []
    if conversation_history:
        for msg in conversation_history:
            if msg["role"] == "user":
                history.append({"human": msg["content"]})
            else:
                history.append({"assistant": msg["content"]})
    
    # Add the current query
    history.append({"human": query})
    
    payload = {
        "chat_history": history,
        "max_new_tokens": 1024,
        "temperature": 0.7
    }
    
    response = make_api_request(API_ENDPOINT, payload)
    
    if "error" in response:
        return {"success": False, "message": response["error"]}
    
    # Extract the assistant's response
    try:
        # Handle based on the API response structure
        if "response" in response:
            return {"success": True, "message": response["response"]}
        elif "assistant" in response:
            return {"success": True, "message": response["assistant"]}
        else:
            return {"success": False, "message": "Unexpected API response format"}
    
    except Exception as e:
        logger.error(f"Error processing API response: {str(e)}")
        return {"success": False, "message": "Error processing response"}

def retrieve_rag_response(user_query: str) -> Dict[str, Any]:
    """
    Generate a response using Retrieval-Augmented Generation (RAG)
    
    Args:
        user_query: The user's input query
        
    Returns:
        API response containing the generated answer
    """
    from utils.constants import RETRIEVE_ENDPOINT
    
    # Prepare payload according to retrieve endpoint documentation
    payload = {
        "user_query": user_query
    }
    
    response = make_api_request(RETRIEVE_ENDPOINT, payload)
    
    if "error" in response:
        return {"success": False, "message": response["error"]}
    
    # Extract response based on API structure
    try:
        if "response" in response:
            return {"success": True, "message": response["response"]}
        else:
            return {"success": False, "message": "Unexpected API response format"}
    
    except Exception as e:
        logger.error(f"Error processing RAG response: {str(e)}")
        return {"success": False, "message": "Error processing RAG response"}

def process_documents(user_query: str, extracted_text: str, token_threshold: int = 8000) -> Dict[str, Any]:
    """
    Process a query against document content
    
    Args:
        user_query: User's query
        extracted_text: Full extracted content from documents
        token_threshold: Max allowed token count before triggering overflow condition
        
    Returns:
        API response with generated answer from documents
    """
    from utils.constants import PROCESS_DOCUMENTS_ENDPOINT
    
    # Prepare payload according to process_documents endpoint documentation
    payload = {
        "user_query": user_query,
        "extracted_text": extracted_text,
        "token_threshold": token_threshold
    }
    
    response = make_api_request(PROCESS_DOCUMENTS_ENDPOINT, payload)
    
    if "error" in response:
        return {"success": False, "message": response["error"]}
    
    # Extract response based on API structure
    try:
        if "response" in response:
            return {"success": True, "message": response["response"]}
        else:
            return {"success": False, "message": "Unexpected API response format"}
    
    except Exception as e:
        logger.error(f"Error processing document API response: {str(e)}")
        return {"success": False, "message": "Error processing document response"}

def check_health() -> bool:
    """
    Check the health status of the API
    
    Returns:
        Boolean indicating if the API is healthy/available
    """
    from utils.constants import HEALTH_ENDPOINT
    
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=3)
        return response.status_code == 200
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return False