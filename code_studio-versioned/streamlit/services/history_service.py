
import json
import os
import streamlit as st
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_history_file_exists():
    """
    Ensure the chat history JSON file exists, create it if it doesn't
    """
    from utils.constants import HISTORY_FILE, DATA_DIR
    
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Create history file with empty structure if it doesn't exist
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump({"conversations": {}}, f)

def load_history():
    """
    Load chat history from the JSON file
    
    Returns:
        Dictionary containing all conversation history
    """
    from utils.constants import HISTORY_FILE
    
    ensure_history_file_exists()
    
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        return history
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading history: {str(e)}")
        return {"conversations": {}}

def save_history(history):
    """
    Save chat history to the JSON file
    
    Args:
        history: Dictionary containing all conversation history
    """
    from utils.constants import HISTORY_FILE
    
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving history: {str(e)}")

def save_message(message, update=False):
    """
    Save a message to the current conversation in history
    
    Args:
        message: Message dictionary to save
        update: Whether this is an update to an existing message
    """
    history = load_history()
    conversation_id = st.session_state.current_conversation_id
    
    # Ensure the conversation exists in history
    if conversation_id not in history["conversations"]:
        history["conversations"][conversation_id] = {
            "title": st.session_state.current_conversation_title,
            "created_at": datetime.now().isoformat(),
            "last_message_at": datetime.now().isoformat(),
            "messages": []
        }
    
    if update:
        # Find and update the message if it exists
        message_idx = None
        for idx, msg in enumerate(history["conversations"][conversation_id]["messages"]):
            if msg.get("timestamp") == message.get("timestamp") and msg.get("role") == message.get("role"):
                message_idx = idx
                break
        
        if message_idx is not None:
            history["conversations"][conversation_id]["messages"][message_idx] = message
        else:
            # If message not found, add it as new
            history["conversations"][conversation_id]["messages"].append(message)
    else:
        # Add new message
        history["conversations"][conversation_id]["messages"].append(message)
    
    # Update last message timestamp
    history["conversations"][conversation_id]["last_message_at"] = datetime.now().isoformat()
    
    save_history(history)

def save_conversation_metadata():
    """
    Save metadata for the current conversation (title, timestamps)
    """
    history = load_history()
    conversation_id = st.session_state.current_conversation_id
    
    # Ensure the conversation exists in history
    if conversation_id not in history["conversations"]:
        history["conversations"][conversation_id] = {
            "title": st.session_state.current_conversation_title,
            "created_at": datetime.now().isoformat(),
            "last_message_at": datetime.now().isoformat(),
            "messages": []
        }
    else:
        # Update existing conversation metadata
        history["conversations"][conversation_id]["title"] = st.session_state.current_conversation_title
        history["conversations"][conversation_id]["last_message_at"] = datetime.now().isoformat()
    
    save_history(history)

def load_user_conversations():
    """
    Load all conversations for the current user
    
    Returns:
        List of conversation metadata for display
    """
    history = load_history()
    conversations = []
    
    for conv_id, conv_data in history["conversations"].items():
        try:
            # Calculate message count
            message_count = len(conv_data.get("messages", []))
            
            # Format the last message timestamp
            last_message_at = datetime.fromisoformat(conv_data.get("last_message_at", datetime.now().isoformat()))
            today = datetime.now().date()
            
            if last_message_at.date() == today:
                formatted_time = f"Today at {last_message_at.strftime('%I:%M %p')}"
            else:
                formatted_time = last_message_at.strftime("%B %d, %Y")
            
            conversations.append({
                "id": conv_id,
                "title": conv_data.get("title", "Untitled Conversation"),
                "last_message": formatted_time,
                "message_count": message_count,
                "timestamp": conv_data.get("last_message_at")  # For sorting
            })
        
        except Exception as e:
            logger.error(f"Error processing conversation {conv_id}: {str(e)}")
    
    # Sort conversations by last message timestamp (most recent first)
    conversations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return conversations

def load_conversation(conversation_id):
    """
    Load a specific conversation and set it as the current conversation
    
    Args:
        conversation_id: ID of the conversation to load
        
    Returns:
        Boolean indicating success or failure
    """
    history = load_history()
    
    if conversation_id in history["conversations"]:
        conversation = history["conversations"][conversation_id]
        
        # Set current conversation details
        st.session_state.current_conversation_id = conversation_id
        st.session_state.current_conversation_title = conversation.get("title", "Untitled Conversation")
        st.session_state.messages = conversation.get("messages", [])
        
        return True
    
    return False

def delete_conversation(conversation_id):
    """
    Delete a conversation from history
    
    Args:
        conversation_id: ID of the conversation to delete
        
    Returns:
        Boolean indicating success or failure
    """
    history = load_history()
    
    if conversation_id in history["conversations"]:
        # Remove the conversation
        del history["conversations"][conversation_id]
        save_history(history)
        
        # If we deleted the current conversation, reset to a new one
        if st.session_state.current_conversation_id == conversation_id:
            from utils.session_state import reset_current_conversation
            reset_current_conversation()
        
        return True
    
    return False