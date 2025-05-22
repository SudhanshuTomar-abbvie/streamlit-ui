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

import streamlit as st
from datetime import datetime
from services.storage_service import load_chat_history, save_chat_history
from services.llm_service import query_llm
from services.document_service import process_document_query

def initialize_chat_state():
    """Initialize session state for chat functionality"""
    # Initialize session state variables
    if 'conversations' not in st.session_state:
        st.session_state.conversations = {}
    if 'current_chat_id' not in st.session_state:
        st.session_state.current_chat_id = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'context' not in st.session_state:
        st.session_state.context = {}
    if 'editing_message_index' not in st.session_state:
        st.session_state.editing_message_index = None
    if 'editing_text' not in st.session_state:
        st.session_state.editing_text = ""
    if 'feedback' not in st.session_state:
        st.session_state.feedback = {}
    if 'show_document_upload' not in st.session_state:
        st.session_state.show_document_upload = False  
    if 'uploaded_documents' not in st.session_state:
        st.session_state.uploaded_documents = []
    if 'thinking' not in st.session_state:
        st.session_state.thinking = False
    if 'response_ready' not in st.session_state:
        st.session_state.response_ready = False
    
    # Load existing chat history if available
    if not st.session_state.conversations:
        loaded_conversations = load_chat_history()
        if loaded_conversations:
            st.session_state.conversations = loaded_conversations
            # Set current_chat_id to the most recent conversation
            st.session_state.current_chat_id = max(
                st.session_state.conversations, 
                key=lambda k: st.session_state.conversations[k]["timestamp"]
            )
            st.session_state.messages = st.session_state.conversations[st.session_state.current_chat_id]["messages"]
            
            # Clear any existing context information to prevent stale data
            st.session_state.context = {}
            
            # Initialize context and feedback for existing messages
            for i, msg in enumerate(st.session_state.messages):
                if msg["role"] == "user":
                    message_id = f"{st.session_state.current_chat_id}_{i}"
                    if "context" in msg:
                        st.session_state.context[message_id] = msg["context"]
                    if "feedback" in msg:
                        st.session_state.feedback[message_id] = msg["feedback"]
        else:
            # Create a default conversation if no history exists
            create_new_chat()

def toggle_document_upload():
    """Toggle document upload panel visibility"""
    st.session_state.show_document_upload = not st.session_state.show_document_upload
    # Clear uploaded documents when hiding the panel
    if not st.session_state.show_document_upload:
        st.session_state.uploaded_documents = []

def clear_uploaded_documents():
    """Clear all uploaded documents"""
    st.session_state.uploaded_documents = []

def process_user_input_with_documents(prompt, document_files):
    """
    Process user input with attached documents
    
    Args:
        prompt (str): User query
        document_files (list): List of uploaded file objects
        
    Returns:
        str: Response text from LLM
    """
    # Process the query with documents
    response_data = process_document_query(document_files, prompt)
    response_text = response_data["response"]
    context = response_data["context"]
    
    # Add user message to chat history with context and document info
    document_names = [doc.name for doc in document_files]
    user_message = {
        "role": "user", 
        "content": prompt,
        "context": context,
        "documents": document_names
    }
    st.session_state.messages.append(user_message)
    
    # Store context in session state
    message_id = f"{st.session_state.current_chat_id}_{len(st.session_state.messages) - 1}"
    st.session_state.context[message_id] = context
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # Update chat title if this is the first message in the conversation
    if len(st.session_state.messages) == 2:  # User message + Assistant response
        update_chat_title(prompt)
    
    # Update the conversations state and save to file
    st.session_state.conversations[st.session_state.current_chat_id]["messages"] = st.session_state.messages
    save_chat_history(st.session_state.conversations)
    
    # Clear uploaded documents after processing
    st.session_state.uploaded_documents = []
    
    return response_text

def create_new_chat():
    """Create a new chat conversation"""
    new_chat_id = datetime.now().strftime("%Y%m%d%H%M%S")
    st.session_state.conversations[new_chat_id] = {
        "title": "New Chat",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": []
    }
    st.session_state.current_chat_id = new_chat_id
    st.session_state.messages = st.session_state.conversations[new_chat_id]["messages"]
    # Clear uploaded documents when creating a new chat
    st.session_state.uploaded_documents = []
    st.session_state.show_document_upload = False

def update_chat_title(message_content):
    """
    Update the title of the current chat
    
    Args:
        message_content (str): First message content to use as title
    """
    title = message_content[:30] + "..." if len(message_content) > 30 else message_content
    if st.session_state.current_chat_id in st.session_state.conversations:
        st.session_state.conversations[st.session_state.current_chat_id]["title"] = title
    else:
        # If key not found, create a new conversation and update the title
        create_new_chat()
        st.session_state.conversations[st.session_state.current_chat_id]["title"] = title

def save_feedback(msg_idx, value):
    """
    Save user feedback on a response
    
    Args:
        msg_idx (int): Message index
        value (str): Feedback value (👍 or 👎)
    """
    message_id = f"{st.session_state.current_chat_id}_{msg_idx}"
    st.session_state.feedback[message_id] = value
    
    # Also save feedback in the conversation data
    if st.session_state.current_chat_id in st.session_state.conversations:
        if msg_idx < len(st.session_state.conversations[st.session_state.current_chat_id]["messages"]):
            st.session_state.conversations[st.session_state.current_chat_id]["messages"][msg_idx]["feedback"] = value
            save_chat_history(st.session_state.conversations)

def start_edit_message(idx):
    """
    Start editing a message
    
    Args:
        idx (int): Message index to edit
    """
    st.session_state.editing_message_index = idx
    st.session_state.editing_text = st.session_state.messages[idx]["content"]

def save_edited_message():
    """Save an edited message and update response if needed"""
    idx = st.session_state.editing_message_index
    if idx is not None and idx < len(st.session_state.messages):
        # Update the message content
        st.session_state.messages[idx]["content"] = st.session_state.editing_text
        
        # If this was a user message, we need to update the assistant's response
        if idx < len(st.session_state.messages) - 1 and st.session_state.messages[idx]["role"] == "user":
            # Get chat history up to this point for context
            chat_history = prepare_chat_history()[:idx]
            
            try:
                # Query LLM with edited message and history
                response_data = query_llm(
                    st.session_state.editing_text,
                    chat_history=chat_history
                )
                
                # Update the assistant's response
                st.session_state.messages[idx + 1]["content"] = response_data["response"]
                
                # Store the context for this message - both in message and session state
                message_id = f"{st.session_state.current_chat_id}_{idx}"
                st.session_state.context[message_id] = response_data["context"]
                st.session_state.messages[idx]["context"] = response_data["context"]
            except Exception as e:
                st.error(f"Failed to update assistant response: {str(e)}")
                # Just keep the original response if we can't update it
        
        # Update the conversations state
        st.session_state.conversations[st.session_state.current_chat_id]["messages"] = st.session_state.messages
        save_chat_history(st.session_state.conversations)
    
    # Reset editing state
    st.session_state.editing_message_index = None
    st.session_state.editing_text = ""

def delete_message(idx):
    """
    Delete a message and its response
    
    Args:
        idx (int): Message index to delete
    """
    if idx < len(st.session_state.messages):
        # If this is a user message, also remove the assistant's response
        if st.session_state.messages[idx]["role"] == "user" and idx + 1 < len(st.session_state.messages):
            st.session_state.messages.pop(idx + 1)  # Remove assistant response
        
        # Remove the message
        st.session_state.messages.pop(idx)
        
        # Update the conversations state
        st.session_state.conversations[st.session_state.current_chat_id]["messages"] = st.session_state.messages
        save_chat_history(st.session_state.conversations)

def cancel_edit():
    """Cancel message editing"""
    st.session_state.editing_message_index = None
    st.session_state.editing_text = ""

def prepare_chat_history():
    """
    Format chat history for LLM
    
    Returns:
        list: Formatted chat history
    """
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages
    ]

def process_user_input(prompt):
    """
    Process user input and get LLM response
    
    Args:
        prompt (str): User input
        
    Returns:
        str: Response text from LLM
    """
    # Prepare chat history for context
    chat_history = prepare_chat_history()
    
    # Get response from LLM
    response_data = query_llm(prompt)
    response_text = response_data["response"]
    context = response_data["context"]
    
    # Generate a unique message ID for the new user message
    msg_idx = len(st.session_state.messages)
    message_id = f"{st.session_state.current_chat_id}_{msg_idx}"
    
    # Add user message to chat history with context
    user_message = {
        "role": "user", 
        "content": prompt,
        "context": context  # Store context directly in message
    }
    st.session_state.messages.append(user_message)
    
    # Also store context in session state with the unique message ID
    st.session_state.context[message_id] = context
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # Update chat title if this is the first message in the conversation
    if len(st.session_state.messages) == 2:  # User message + Assistant response
        update_chat_title(prompt)
    
    # Update the conversations state and save to file
    st.session_state.conversations[st.session_state.current_chat_id]["messages"] = st.session_state.messages
    save_chat_history(st.session_state.conversations)
    
    return response_text