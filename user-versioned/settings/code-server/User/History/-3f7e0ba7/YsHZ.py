import streamlit as st
import uuid
from datetime import datetime

def init_session_state():
    """
    Initialize all session state variables if they don't exist
    """
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    if 'health_status' not in st.session_state:
        st.session_state.health_status = True
    
    if 'current_conversation_id' not in st.session_state:
        st.session_state.current_conversation_id = str(uuid.uuid4())
    
    if 'current_conversation_title' not in st.session_state:
        st.session_state.current_conversation_title = f"New Conversation ({datetime.now().strftime('%B %d, %Y')})"
    
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "id": "user_001"
        }
    
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            "email_notifications": True,
            "weekly_reports": False,
            "message_size": "Medium",
            "theme_color": "#2e3191"
        }
    
    if 'uploaded_documents' not in st.session_state:
        st.session_state.uploaded_documents = []

def reset_current_conversation():
    """
    Reset the current conversation to start a new one
    """
    st.session_state.messages = []
    st.session_state.current_conversation_id = str(uuid.uuid4())
    st.session_state.current_conversation_title = f"New Conversation ({datetime.now().strftime('%B %d, %Y')})"