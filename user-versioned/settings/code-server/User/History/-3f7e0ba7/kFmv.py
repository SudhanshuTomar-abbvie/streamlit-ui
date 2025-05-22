import streamlit as st
import uuid
from datetime import datetime

def init_session_state():
    """Initialize all session state variables"""
    # Chat-related session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = str(uuid.uuid4())
    
    if "current_conversation_title" not in st.session_state:
        st.session_state.current_conversation_title = "New Conversation"
    
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    
    # UI-related session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    
    # Document-related session state
    if "doc_query_mode" not in st.session_state:
        st.session_state.doc_query_mode = False
    
    if "extracted_doc_text" not in st.session_state:
        st.session_state.extracted_doc_text = None
    
    # Input-related session state
    if "user_input_text" not in st.session_state:
        st.session_state.user_input_text = ""
    
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False

def reset_current_conversation():
    """Reset the current conversation to start a new one"""
    st.session_state.current_conversation_id = str(uuid.uuid4())
    st.session_state.current_conversation_title = "New Conversation"
    st.session_state.chat_history = []
    
    # Clear any document-related state
    st.session_state.doc_query_mode = False
    st.session_state.extracted_doc_text = None
    if "active_doc_name" in st.session_state:
        del st.session_state.active_doc_name
    
    # Clear input state
    st.session_state.user_input_text = ""
    
    # Clear any temporary states
    if "temp_user_input" in st.session_state:
        del st.session_state.temp_user_input
    if "pending_user_input" in st.session_state:
        del st.session_state.pending_user_input

def start_new_conversation():
    """Start a new conversation and navigate to chat page"""
    reset_current_conversation()
    st.session_state.current_page = "chat"

def ensure_conversation_sync():
    """Ensure conversation is synced to history file"""
    from services.history_service import sync_conversation_to_history
    sync_conversation_to_history()