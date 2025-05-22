

import streamlit as st
import logging
from services.history_service import load_user_conversations, load_conversation, delete_conversation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_history_page():
    """
    Render the conversation history page
    """
    st.header("Conversation History")
    
    st.markdown("<h3>Review your previous conversations with MLOPS Chatbot.</h3>", unsafe_allow_html=True)
    
    # Load all conversations
    conversations = load_user_conversations()
    
    if not conversations:
        st.info("You don't have any saved conversations yet. Start chatting to create one!")
        
        # Add a button to go to chat
        if st.button("Start New Conversation"):
            st.session_state.current_page = "chat"
            st.rerun()
        
        return
    
    # Display conversations
    for i, conversation in enumerate(conversations):
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{conversation['title']}**")
                st.markdown(f"Last message: {conversation['last_message']}")
            
            with col2:
                st.markdown(f"{conversation['message_count']} messages")
            
            with col3:
                # Actions
                if st.button("View", key=f"view_conv_{i}"):
                    # Load this conversation
                    load_conversation(conversation['id'])
                    
                    # Go to chat page
                    st.session_state.current_page = "chat"
                    st.rerun()
                
                if st.button("Delete", key=f"delete_conv_{i}"):
                    # Delete this conversation
                    delete_conversation(conversation['id'])
                    st.success(f"Conversation '{conversation['title']}' deleted.")
                    st.rerun()
            
            st.markdown("---")
    
    # Add a button to start a new conversation
    if st.button("Start New Conversation", key="start_new_conv"):
        from utils.session_state import reset_current_conversation
        reset_current_conversation()
        st.session_state.current_page = "chat"
        st.rerun()