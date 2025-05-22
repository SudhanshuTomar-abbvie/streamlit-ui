import streamlit as st
from datetime import datetime
import logging
from services.api_service import generate_chat_response, process_document_query
from services.history_service import save_message, save_conversation_metadata
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_message(message: str, is_document_query: bool = False) -> bool:
    """
    Handle a new message from the user
    
    Args:
        message: User's message content
        is_document_query: Whether this is a query against uploaded documents
        
    Returns:
        Boolean indicating success or failure
    """
    if not message.strip():  # Ignore empty messages
        return False
    
    # Add user message to chat
    user_message = {"role": "user", "content": message, "timestamp": datetime.now().isoformat()}
    st.session_state.messages.append(user_message)
    
    # Save the user message to history
    save_message(user_message)
    
    # Generate response based on the query type
    if is_document_query and st.session_state.uploaded_documents:
        logger.info("Processing document query")
        response = process_document_query(message, st.session_state.uploaded_documents)
    else:
        logger.info("Processing regular chat query")
        # response = generate_chat_response(message, st.session_state.messages)
        response = generate_chat_response(message)
        # if response:
        #     display_response(response["message"])
        # else:
        #     st.error(response["message"])
    
    # Handle the response
    if response["success"]:
        # Add bot response to chat
        bot_message = {
            "role": "assistant", 
            "content": response["message"], 
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.messages.append(bot_message)
        
        # Save the bot message to history
        save_message(bot_message)
        
        # Update conversation metadata
        save_conversation_metadata()
        
        return True
    else:
        # Add error message to chat
        error_message = {
            "role": "assistant", 
            "content": f"I'm sorry, I encountered an error: {response['message']}. Please try again.", 
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.messages.append(error_message)
        
        # Save the error message to history
        save_message(error_message)
        
        return False

def update_message(message_index: int, new_content: str) -> bool:
    """
    Update a message in the current conversation
    
    Args:
        message_index: Index of the message to update
        new_content: New content for the message
        
    Returns:
        Boolean indicating success or failure
    """
    if 0 <= message_index < len(st.session_state.messages):
        # Update the message content
        st.session_state.messages[message_index]["content"] = new_content
        st.session_state.messages[message_index]["edited"] = True
        st.session_state.messages[message_index]["edit_timestamp"] = datetime.now().isoformat()
        
        # Save the updated message to history
        save_message(st.session_state.messages[message_index], update=True)
        
        return True
    
    return False

def delete_message(message_index: int) -> bool:
    """
    Delete a message from the current conversation
    
    Args:
        message_index: Index of the message to delete
        
    Returns:
        Boolean indicating success or failure
    """
    if 0 <= message_index < len(st.session_state.messages):
        # Remove the message
        deleted_message = st.session_state.messages.pop(message_index)
        
        # Update the conversation in history
        save_conversation_metadata()
        
        return True
    
    return False

def change_conversation_title(new_title: str) -> bool:
    """
    Change the title of the current conversation
    
    Args:
        new_title: New title for the conversation
        
    Returns:
        Boolean indicating success or failure
    """
    if new_title.strip():
        st.session_state.current_conversation_title = new_title
        save_conversation_metadata()
        return True
    
    return False

def get_formatted_messages() -> List[Dict[str, Any]]:
    """
    Get messages in a user-friendly format for display
    
    Returns:
        List of messages with formatted timestamps
    """
    formatted_messages = []
    
    for msg in st.session_state.messages:
        formatted_msg = msg.copy()
        
        # Format the timestamp
        if "timestamp" in msg:
            try:
                timestamp = datetime.fromisoformat(msg["timestamp"])
                formatted_msg["formatted_time"] = timestamp.strftime("%I:%M %p")
                formatted_msg["formatted_date"] = timestamp.strftime("%B %d, %Y")
            except (ValueError, TypeError):
                formatted_msg["formatted_time"] = ""
                formatted_msg["formatted_date"] = ""
        
        formatted_messages.append(formatted_msg)
    
    return formatted_messages

# Add this function to your services/chat_service.py file

def create_new_conversation():
    """Create a new conversation and reset the current session"""
    from utils.session_state import reset_current_conversation
    # Save current conversation if needed
    # TODO: Add code to save the current conversation to history
    
    # Reset for new conversation
    reset_current_conversation()
    
    # Set default title
    from datetime import datetime
    st.session_state.current_conversation_title = f"Conversation {datetime.now().strftime('%b %d, %Y')}"