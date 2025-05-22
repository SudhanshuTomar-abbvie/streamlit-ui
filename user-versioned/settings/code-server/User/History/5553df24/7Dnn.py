# Modified chat_service.py
import streamlit as st
import time
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.text_extractor import handle_query

def init_chat_session():
    """Initialize the chat session if not already initialized"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = str(uuid.uuid4())
    
    if "current_conversation_title" not in st.session_state:
        st.session_state.current_conversation_title = "New Conversation"
    
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}

def handle_message(user_message: str, custom_response: Optional[str] = None):
    """
    Process user message and get response from API or from document query
    
    Args:
        user_message: The user's input
        custom_response: Optional pre-generated response (for document queries)
    """
    init_chat_session()
    
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    
    # If we have a custom response (e.g., from document query), use it
    if custom_response:
        # Add the custom response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": custom_response,
            "timestamp": datetime.now().isoformat()
        })
        return
    
    # Handle regular or document-based query
    use_document_mode = st.session_state.get("doc_query_mode", False)
    
    with st.spinner("Thinking..."):
        # Get response using appropriate method
        response = handle_query(user_message, use_document_mode)
        
        # Add response to chat history
        if response.get("success", False):
            assistant_message = response.get("message", "")
            context = response.get("context", None)
            
            message_data = {
                "role": "assistant",
                "content": assistant_message,
                "timestamp": datetime.now().isoformat()
            }
            
            if context:
                message_data["context"] = context
                
            st.session_state.chat_history.append(message_data)
        else:
            error_message = response.get("message", "Sorry, I encountered an error processing your request.")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_message,
                "timestamp": datetime.now().isoformat()
            })
    
    # Save conversation
    save_current_conversation()

def get_formatted_messages() -> List[Dict[str, Any]]:
    """
    Get the message history for the current conversation
    
    Returns:
        List of message dictionaries with role and content
    """
    init_chat_session()
    return st.session_state.chat_history

def change_conversation_title(new_title: str):
    """Update the current conversation title"""
    st.session_state.current_conversation_title = new_title
    save_current_conversation()

def save_current_conversation():
    """Save the current conversation to the conversations dictionary"""
    if "current_conversation_id" not in st.session_state:
        return
    
    conversation_id = st.session_state.current_conversation_id
    
    st.session_state.conversations[conversation_id] = {
        "id": conversation_id,
        "title": st.session_state.current_conversation_title,
        "messages": st.session_state.chat_history.copy(),
        "updated_at": datetime.now().isoformat()
    }

def load_conversation(conversation_id: str):
    """Load a conversation from the history by ID"""
    if conversation_id not in st.session_state.conversations:
        return False
    
    st.session_state.current_conversation_id = conversation_id
    st.session_state.current_conversation_title = st.session_state.conversations[conversation_id]["title"]
    st.session_state.chat_history = st.session_state.conversations[conversation_id]["messages"].copy()
    
    return True

def delete_message(index: int):
    """Delete a message from the current conversation"""
    if 0 <= index < len(st.session_state.chat_history):
        st.session_state.chat_history.pop(index)
        save_current_conversation()
        return True
    return False

def update_message(index: int, new_content: str):
    """Update a message in the current conversation"""
    if 0 <= index < len(st.session_state.chat_history):
        st.session_state.chat_history[index]["content"] = new_content
        save_current_conversation()
        return True
    return False