import streamlit as st
import threading
import time
import logging
from services.api_service import check_health

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variable to track if the health check thread is running
health_check_thread_running = False

def start_health_check_thread():
    """
    Start a background thread that periodically checks API health status
    """
    global health_check_thread_running
    
    if health_check_thread_running:
        return
    
    health_check_thread_running = True
    
    def health_check_worker():
        """Background worker function to check API health"""
        from utils.constants import HEALTH_CHECK_INTERVAL
        
        global health_check_thread_running
        
        logger.info("Starting health check thread")
        
        try:
            while health_check_thread_running:
                # Check API health
                is_healthy = check_health()
                
                # Update session state
                st.session_state.health_status = is_healthy
                
                # Sleep for the defined interval
                time.sleep(HEALTH_CHECK_INTERVAL)
        
        except Exception as e:
            logger.error(f"Health check thread error: {str(e)}")
            st.session_state.health_status = False
        
        logger.info("Health check thread stopped")
    
    # Start the thread
    thread = threading.Thread(target=health_check_worker, daemon=True)
    thread.start()

def stop_health_check_thread():
    """
    Stop the health check background thread
    """
    global health_check_thread_running
    health_check_thread_running = False

def get_health_status():
    """
    Get the current health status
    
    Returns:
        Current health status from session state
    """
    return st.session_state.health_status

def check_health_now():
    """
    Perform an immediate health check and update session state
    
    Returns:
        Current health status
    """
    is_healthy = check_health()
    st.session_state.health_status = is_healthy
    return is_healthy