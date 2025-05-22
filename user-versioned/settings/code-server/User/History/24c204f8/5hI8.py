import streamlit as st
from datetime import datetime
from components.chat_message import render_message_editor
from services.chat_service import (
    handle_message,
    get_formatted_messages,
    change_conversation_title,
    delete_message,
    update_message
)
from services.document_service import get_uploaded_documents, process_uploaded_file
from utils.session_state import reset_current_conversation

def render_chat_page():
    # Chat interface container structure
    st.markdown("""
        <style>
        /* Main container for better spacing */
        .main-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            max-width: 100%;
            padding-bottom: 80px;
        }
        
        /* Header styles */
        .header-container {
            padding: 1rem 0;
        }
        
        /* Messages container with scrolling */
        .messages-container {
            flex-grow: 1;
            overflow-y: auto;
            padding-bottom: 120px; /* Space for input */
        }
        
        /* Fixed input container at bottom */
        .input-container {
            position: fixed;
            bottom: 40px;
            left: 0;
            right: 0;
            background-color: white;
            padding: 10px;
            z-index: 100;
            border-top: 1px solid #f0f0f0;
        }
        
        /* Footer styles */
        footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 40px;
            background-color: white;
            z-index: 999;
            padding: 10px;
            text-align: center;
            font-size: 0.8rem;
            color: gray;
            border-top: 1px solid #f0f0f0;
        }
        
        /* Better styling for message editing buttons */
        .edit-buttons {
            opacity: 0.6;
            font-size: 0.8rem;
        }
        .edit-buttons:hover {
            opacity: 1;
        }
        
        /* Ensure Streamlit components play nicely with our layout */
        .stChatInputContainer, .stChatFloatingInputContainer {
            position: relative !important;
            bottom: auto !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header section
    with st.container():
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        
        # Chat title with input
        current_title = st.session_state.current_conversation_title
        new_title = st.text_input("Chat Title", value=current_title, key="chat_title_input")
        if new_title != current_title:
            change_conversation_title(new_title)
        
        st.caption(f"🕓 Last updated: {datetime.now().strftime('%I:%M:%S %p')}")
        
        # Document upload section - toggled by pin button
        if "show_uploader" not in st.session_state:
            st.session_state.show_uploader = False
            
        if st.session_state.show_uploader:
            uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
            if uploaded_file:
                processed = process_uploaded_file(uploaded_file)
                if processed:
                    st.success(f"Uploaded: {processed['name']}")
                    # Auto-hide uploader after successful upload
                    st.session_state.show_uploader = False
                    st.rerun()
                else:
                    st.error("Failed to process uploaded document")
        
        # Show info about uploaded documents
        docs = get_uploaded_documents()
        if docs:
            st.info(f"📄 {len(docs)} document{'s' if len(docs)>1 else ''} uploaded")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Editor for message editing
    is_editing = render_message_editor()
    
    # Main messages container
    st.markdown('<div class="messages-container">', unsafe_allow_html=True)
    
    # Render all chat messages
    if not is_editing:
        messages = get_formatted_messages()
        for i, msg in enumerate(messages):
            with st.chat_message(msg["role"]):
                st.markdown(f"{msg['content']}")
                
                # Small, subtle edit/delete buttons with better styling
                col1, col2, col3 = st.columns([0.94, 0.03, 0.03])
                with col2:
                    if st.button("✏️", key=f"edit_{i}", help="Edit", use_container_width=True):
                        st.session_state.edit_index = i
                        st.session_state.edit_content = msg["content"]
                        st.rerun()
                with col3:
                    if st.button("🗑️", key=f"del_{i}", help="Delete", use_container_width=True):
                        delete_message(i)
                        st.rerun()
    
    # In-place edit form
    if "edit_index" in st.session_state:
        with st.container():
            new_txt = st.text_area("Edit Message", value=st.session_state.edit_content, height=100)
            cols = st.columns([0.5, 0.5])
            with cols[0]:
                if st.button("💾 Save", use_container_width=True):
                    update_message(st.session_state.edit_index, new_txt)
                    del st.session_state.edit_index
                    del st.session_state.edit_content
                    st.rerun()
            with cols[1]:
                if st.button("❌ Cancel", use_container_width=True):
                    del st.session_state.edit_index
                    del st.session_state.edit_content
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fixed input container at bottom
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    input_cols = st.columns([0.08, 0.92])
    with input_cols[0]:
        if st.button("📎", key="toggle_upload"):
            st.session_state.show_uploader = not st.session_state.show_uploader
            st.rerun()
    with input_cols[1]:
        # The key component - using st.chat_input which properly manages message history
        user_input = st.chat_input("Type your message…")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle user submission
    if user_input:
        # Add user message to chat
        with st.chat_message("user"):
            st.markdown(user_input)
            
        # Show AI thinking with spinner
        with st.chat_message("assistant"):
            with st.spinner("Pondering..."):
                # Process the message
                handle_message(user_input, is_document_query=bool(docs))
                st.rerun()
    
    # Footer
    st.markdown("""
        <footer>
            Powered by MLOPS Chatbot
        </footer>
    """, unsafe_allow_html=True)