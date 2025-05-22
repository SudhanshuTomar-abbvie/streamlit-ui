#chat_message.py
import streamlit as st
from utils.rendering import render_svg
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_chat_messages(messages, logo_path="assets/avatarlogo.svg"):
    """
    Render chat messages in the chat container
    
    Args:
        messages: List of message dictionaries to render
        logo_path: Path to the logo/avatar SVG file
    """
    # Get SVG content for the bot avatar
    img_content = render_svg(logo_path)
    
    # Start chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not messages:
        # Initial welcome message with logo
        st.markdown(
            f'''
            <div class="message bot-message">
                <div class="avatar bot-avatar">{img_content}</div>
                <div class="message-content">
                    MLOPS Chatbot is ready to assist you<br>
                    Ask a question about patient touchpoints or healthcare experiences
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
    else:
        # Display all messages
        for idx, message in enumerate(messages):
            if message["role"] == "user":
                # Show user message with edit/delete options
                with st.container():
                    col1, col2 = st.columns([0.9, 0.1])
                    
                    with col1:
                        st.markdown(
                            f'''
                            <div class="message user-message">
                                <div class="message-content">{message["content"]}</div>
                                <div class="avatar user-avatar">JD</div>
                            </div>
                            ''',
                            unsafe_allow_html=True
                        )
                    
                    with col2:
                        # Add edit/delete options in a dropdown
                        with st.expander("⋮", expanded=False):
                            if st.button("✏️ Edit", key=f"edit_msg_{idx}"):
                                st.session_state.editing_message_idx = idx
                                st.session_state.editing_message_content = message["content"]
                                st.rerun()
                            
                            if st.button("🗑️ Delete", key=f"delete_msg_{idx}"):
                                from services.chat_service import delete_message
                                delete_message(idx)
                                st.rerun()
            else:
                # Show assistant message
                st.markdown(
                    f'''
                    <div class="message bot-message">
                        <div class="avatar bot-avatar">{img_content}</div>
                        <div class="message-content">{message["content"]}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_message_editor():
    """
    Render the message editing interface if a message is being edited
    
    Returns:
        True if rendering the editor, False otherwise
    """
    if hasattr(st.session_state, 'editing_message_idx') and st.session_state.editing_message_idx is not None:
        st.markdown("<h4>Edit Message</h4>", unsafe_allow_html=True)
        
        # Get message index
        idx = st.session_state.editing_message_idx
        
        # Show editor
        new_content = st.text_area(
            "Edit your message:", 
            value=st.session_state.editing_message_content,
            height=100,
            key="edit_message_content"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Save Changes"):
                from services.chat_service import update_message
                update_message(idx, new_content)
                
                # Reset editing state
                st.session_state.editing_message_idx = None
                st.session_state.editing_message_content = None
                
                st.rerun()
        
        with col2:
            if st.button("Cancel"):
                # Reset editing state
                st.session_state.editing_message_idx = None
                st.session_state.editing_message_content = None
                
                st.rerun()
        
        return True
    
    return False

def render_chat_input():
    """
    Render the chat input area
    
    Returns:
        User input text if the send button is clicked, None otherwise
    """
    # Input field section fixed at the bottom
    st.markdown('<div class="chat-footer">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown('<div class="input-field">', unsafe_allow_html=True)
        user_input = st.text_input(
            label="",
            placeholder="Ask MLOPS Chatbot about patient touchpoints...",
            key="chat_input",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="input-button">', unsafe_allow_html=True)
        send_clicked = st.button("Send", key="send_button")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close chat-footer
    
    if send_clicked and user_input:
        return user_input
    
    return None

# Add these functions to your components/chat_message.py file

def render_message_actions(message):
    """Render action buttons for a chat message"""
    if "actions" not in message:
        return ""
    
    actions_html = '<div class="message-actions">'
    for action in message["actions"]:
        actions_html += f'<button class="message-action-btn" data-action="{action["action"]}" data-id="{action["id"]}">{action["label"]}</button>'
    actions_html += '</div>'
    
    return actions_html

def render_chat_input(include_resend=False):
    """Render the chat input area with optional resend button"""
    col1, col2 = st.columns([8, 1]) if include_resend else [st.container(), None]
    
    with col1:
        user_input = st.text_area(
            "Message",
            key="user_input",
            height=80,
            placeholder="Type your message here...",
            label_visibility="collapsed",
        )
    
    resend_clicked = False
    if include_resend and col2:
        with col2:
            st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)  # Add spacing
            resend_clicked = st.button("↻", help="Resend last message", use_container_width=True)
    
    return user_input, resend_clicked if include_resend else user_input