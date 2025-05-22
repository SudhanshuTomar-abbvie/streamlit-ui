#api_service.py
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


def generate_chat_response(user_query: str) -> Dict[str, Any]:
    """
    Generate a response by calling the Dataiku Webapp backend API.   
    Args:
        user_query: The user's input query.
    Returns:
        Dict with 'success', 'message', and optional 'context'.
    """
    import dataiku

    DSS_LOCATION = "https://cdl-dku-desi-p.commercial-datalake-prod.awscloud.abbvienet.com"
    API_KEY = "dkuaps-9ALuuZLhFJg9dTcrSgPMcsdtfP8bpPXC"
    PROJECT_KEY = "GENAIPOC"
    WEBAPP_ID = "LmdRX0E"
    
    dataiku.set_remote_dss(DSS_LOCATION, API_KEY, no_check_certificate=True)
    
    try:
        client = dataiku.api_client()
        project = client.get_project(PROJECT_KEY)
        webapp = project.get_webapp(WEBAPP_ID)
        backend = webapp.get_backend_client()
        backend.session.headers['Content-Type'] = 'application/json'

        response = backend.session.post(
            backend.base_url + '/query',
            json={'message': user_query}
        )

        if response.status_code == 200:
            try:
                response_data = response.json()
                answer = response_data.get("message", "")
                context = response_data.get("context", "")
                return {
                    "success": response_data.get("success", True),
                    "message": answer,
                    "context": context
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "message": response.text
                }
        else:
            return {
                "success": False,
                "message": f"Error: {response.status_code} - {response.text}"
            }

    except Exception as e:
        logger.error(f"Failed to get response from Dataiku webapp: {str(e)}")
        return {
            "success": False,
            "message": f"Internal error: {str(e)}"
        }



def process_document_query(user_query: str, extracted_text: str, token_threshold: int = 8000) -> Dict[str, Any]:
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