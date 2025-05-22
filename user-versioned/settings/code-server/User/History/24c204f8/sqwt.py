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
    # Create a clean layout with proper spacing using Streamlit's built-in containers
    
    # Header section with title and timestamp
    with st.container():
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            current_title = st.session_state.current_conversation_title
            new_title = st.text_input("Chat Title", value=current_title, key="chat_title_input")
            if new_title != current_title:
                change_conversation_title(new_title)
        with col2:
            st.caption(f"🕓 Last updated: {datetime.now().strftime('%I:%M:%S %p')}")
    
    # Document upload section - hidden by default until pin is clicked
    if st.session_state.get("show_uploader", False):
        with st.container():
            uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
            if uploaded_file:
                processed = process_uploaded_file(uploaded_file)
                if processed:
                    st.success(f"Uploaded: {processed['name']}")
                else:
                    st.error("Failed to process uploaded document")
    
    # Show info about uploaded documents
    docs = get_uploaded_documents()
    if docs:
        st.info(f"📄 {len(docs)} document{'s' if len(docs)>1 else ''} uploaded")
    
    # Messages area
    message_container = st.container()
    
    # Render editor if active
    is_editing = render_message_editor()
    
    # Display chat messages
    with message_container:
        if not is_editing:
            for i, msg in enumerate(get_formatted_messages()):
                with st.chat_message(msg["role"]):
                    st.markdown(f"**{msg['role'].capitalize()}** ({msg['formatted_time']}): {msg['content']}")
                    
                    # Action buttons in a single line
                    cols = st.columns([0.9, 0.05, 0.05])
                    with cols[1]:
                        if st.button("✏️", key=f"edit_{i}", help="Edit"):
                            st.session_state.edit_index = i
                            st.session_state.edit_content = msg["content"]
                            st.rerun()
                    with cols[2]:
                        if st.button("🗑️", key=f"del_{i}", help="Delete"):
                            delete_message(i)
                            st.rerun()
    
    # In-place edit form
    if "edit_index" in st.session_state:
        with st.container():
            new_txt = st.text_area("Edit Message", value=st.session_state.edit_content)
            save_col, cancel_col = st.columns(2)
            with save_col:
                if st.button("💾 Save", use_container_width=True):
                    update_message(st.session_state.edit_index, new_txt)
                    del st.session_state.edit_index
                    del st.session_state.edit_content
                    st.rerun()
            with cancel_col:
                if st.button("❌ Cancel", use_container_width=True):
                    del st.session_state.edit_index
                    del st.session_state.edit_content
                    st.rerun()
    
    # Add minimal space before chat input
    st.write("")
    
    # Chat input with attachment toggle
    input_cols = st.columns([0.1, 0.9])
    with input_cols[0]:
        if st.button("📎", key="toggle_upload"):
            st.session_state.show_uploader = not st.session_state.get("show_uploader", False)
            st.rerun()
    with input_cols[1]:
        user_input = st.chat_input("Type your message…")
    
    # Handle user submission
    if user_input:
        handle_message(user_input, is_document_query=bool(docs))
        st.rerun()
    
    # Compact footer
    st.caption("Powered by MLOPS Chatbot", help="BTS Patient Services")