import requests
import streamlit as st
import logging
from config.settings import BACKEND_API_BASE_URL

def get_health_status():
    """
    Call the backend health check endpoint to get service status
    
    Returns:
        dict: Health status information or error message
    """
    try:
        # Construct the health check endpoint URL
        health_endpoint = f"{BACKEND_API_BASE_URL}/chat/health/run"f"{BACKEND_API_BASE_URL}
        
        # Make GET request to health check endpoint
        response = requests.get(health_endpoint, timeout=5)
        response.raise_for_status()
        
        # Return the health data
        return {
            "status": "connected",
            "data": response.json(),
            "error": None
        }
    except requests.RequestException as e:
        logging.error(f"Health check failed: {str(e)}")
        return {
            "status": "disconnected",
            "data": None,
            "error": f"Connection error: {str(e)}"
        }
    except Exception as e:
        logging.error(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "data": None, 
            "error": f"Error: {str(e)}"
        }