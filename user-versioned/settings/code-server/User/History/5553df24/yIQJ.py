import streamlit as st
import time
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.text_extractor import handle_query
from services.history_service import save_message, save_conversation_metadata

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

def generate_conversation_title(user_message: str) -> str:
    """
    Generate a conversation title based on the first user message
    
    Args:
        user_message: The first user message
        
    Returns:
        Generated title (first 50 chars or meaningful summary)
    """
    # Remove extra whitespace and newlines
    cleaned_message = ' '.join(user_message.strip().split())
    
    # If message is short enough, use it as title
    if len(cleaned_message) <= 50:
        return cleaned_message
    
    # Otherwise, take first 47 chars and add "..."
    return cleaned_message[:47] + "..."

def stream_response(response_text: str, placeholder):
    """
    Stream response word by word
    
    Args:
        response_text: Complete response text
        placeholder: Streamlit placeholder to update
    """
    words = response_text.split()
    displayed_text = ""
    
    for word in words:
        displayed_text += word + " "
        placeholder.markdown(displayed_text)
        time.sleep(0.05)  # Adjust speed as needed
    
    return displayed_text.strip()

def handle_message(user_message: str, custom_response: Optional[str] = None, is_edit: bool = False, edit_index: Optional[int] = None):
    """
    Process user message and get response from API or from document query
    
    Args:
        user_message: The user's input
        custom_response: Optional pre-generated response (for document queries)
        is_edit: Whether this is an edit operation
        edit_index: Index of the message being edited (for edit operations)
    """
    init_chat_session()
    
    # If this is an edit operation
    if is_edit and edit_index is not None:
        # Update the user message at the specified index
        if 0 <= edit_index < len(st.session_state.chat_history):
            st.session_state.chat_history[edit_index]["content"] = user_message
            st.session_state.chat_history[edit_index]["timestamp"] = datetime.now().isoformat()
            
            # Remove the assistant's response that follows (if it exists)
            if edit_index + 1 < len(st.session_state.chat_history) and \
               st.session_state.chat_history[edit_index + 1]["role"] == "assistant":
                st.session_state.chat_history.pop(edit_index + 1)
        
        # Save the updated message to history file
        save_message(st.session_state.chat_history[edit_index], update=True)
    else:
        # Add new user message to history
        user_msg = {
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.chat_history.append(user_msg)
        
        # Save user message to history file
        save_message(user_msg)
        
        # Auto-generate conversation title if this is the first message
        if len(st.session_state.chat_history) == 1:  # First user message
            new_title = generate_conversation_title(user_message)
            st.session_state.current_conversation_title = new_title
            save_conversation_metadata()
    
    # If we have a custom response (e.g., from document query), use it
    if custom_response:
        assistant_msg = {
            "role": "assistant",
            "content": custom_response,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.chat_history.append(assistant_msg)
        save_message(assistant_msg)
        return custom_response
    
    # Handle regular or document-based query
    use_document_mode = st.session_state.get("doc_query_mode", False)
    
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
        save_message(message_data)
        
        return assistant_message
    else:
        error_message = response.get("message", "Sorry, I encountered an error processing your request.")
        assistant_msg = {
            "role": "assistant",
            "content": error_message,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.chat_history.append(assistant_msg)
        save_message(assistant_msg)
        
        return error_message

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
    save_conversation_metadata()

def save_current_conversation():
    """Save the current conversation to the conversations dictionary and history file"""
    if "current_conversation_id" not in st.session_state:
        return
    
    conversation_id = st.session_state.current_conversation_id
    
    # Update in-memory conversations
    st.session_state.conversations[conversation_id] = {
        "id": conversation_id,
        "title": st.session_state.current_conversation_title,
        "messages": st.session_state.chat_history.copy(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Save metadata to history file
    save_conversation_metadata()

def load_conversation(conversation_id: str):
    """Load a conversation from the history by ID"""
    from services.history_service import load_conversation as load_conv_from_file
    return load_conv_from_file(conversation_id)

def delete_message(index: int):
    """Delete a message from the current conversation"""
    if 0 <= index < len(st.session_state.chat_history):
        # If deleting a user message, also delete the following assistant message if it exists
        if (st.session_state.chat_history[index]["role"] == "user" and 
            index + 1 < len(st.session_state.chat_history) and 
            st.session_state.chat_history[index + 1]["role"] == "assistant"):
            # Remove both user and assistant messages
            st.session_state.chat_history.pop(index + 1)
            st.session_state.chat_history.pop(index)
        else:
            st.session_state.chat_history.pop(index)
        
        save_current_conversation()
        return True
    return False

def update_message(index: int, new_content: str):
    """Update a message in the current conversation and regenerate response if it's a user message"""
    if 0 <= index < len(st.session_state.chat_history):
        message = st.session_state.chat_history[index]
        
        # If it's a user message, regenerate the assistant response
        if message["role"] == "user":
            # Use handle_message with edit parameters
            return handle_message(new_content, is_edit=True, edit_index=index)
        else:
            # For assistant messages, just update the content
            st.session_state.chat_history[index]["content"] = new_content
            st.session_state.chat_history[index]["timestamp"] = datetime.now().isoformat()
            save_message(st.session_state.chat_history[index], update=True)
            return True
    return False