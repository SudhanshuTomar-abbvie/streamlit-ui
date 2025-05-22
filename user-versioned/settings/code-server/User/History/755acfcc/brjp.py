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



def process_document_query(file_list: list) -> Dict[str, Any]:
    """
    Sends uploaded files to the /query_on_docs endpoint on Dataiku webapp.

    Args:
        file_list (list): List of files, where each file is a dict with 'filename' and 'content' (base64 encoded).

    Returns:
        Dict with 'success', 'message', and optional 'result'.
    """
    import dataiku
    import json
    import logging

    logger = logging.getLogger(__name__)

    DSS_LOCATION = "https://cdl-dku-desi-p.commercial-datalake-prod.awscloud.abbvienet.com"
    API_KEY = "dkuaps-9ALuuZLhFJg9dTcrSgPMcsdtfP8bpPXC"
    PROJECT_KEY = "GENAIPOC"
    WEBAPP_ID = "LmdRX0E"

    try:
        # Setup DSS connection
        dataiku.set_remote_dss(DSS_LOCATION, API_KEY, no_check_certificate=True)

        # Connect to webapp
        client = dataiku.api_client()
        project = client.get_project(PROJECT_KEY)
        webapp = project.get_webapp(WEBAPP_ID)
        backend = webapp.get_backend_client()
        backend.session.headers['Content-Type'] = 'application/json'

        # Prepare and send payload to /query_on_docs
        payload = {"files": file_list}
        response = backend.session.post(backend.base_url + '/query_on_docs', json=payload)

        if response.status_code == 200:
            response_data = response.json()
            return {
                "success": True,
                "combined_text": response_data.get("combined_text", ""),
                "result": response_data.get("result", {}),
                "file_count": response_data.get("file_count", 0)
            }
        else:
            return {
                "success": False,
                "message": f"Error: {response.status_code} - {response.text}"
            }

    except Exception as e:
        logger.error(f"Failed to call /query_on_docs: {str(e)}")
        return {
            "success": False,
            "message": f"Internal error: {str(e)}"
        }


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