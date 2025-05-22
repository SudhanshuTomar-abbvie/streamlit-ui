import streamlit as st
from datetime import datetime
from components.chat_message import render_message_editor
from services.chat_service import handle_message, get_formatted_messages, change_conversation_title
from services.document_service import get_uploaded_documents
from utils.session_state import reset_current_conversation

def render_chat_page():
    st.title("🧠 Chat Assistant")

    # Chat title
    current_title = st.session_state.current_conversation_title
    new_title = st.text_input("Chat Title", value=current_title, key="chat_title_input")
    if new_title != current_title:
        change_conversation_title(new_title)

    # Timestamp and doc info
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S %p')}")

    # Uploaded documents info
    docs = get_uploaded_documents()
    if docs:
        st.info(f"📄 {len(docs)} document{'s' if len(docs) > 1 else ''} uploaded")

    # Show editor if needed
    is_editing = render_message_editor()

        # Chat messages
    if not is_editing:
        messages = get_formatted_messages()
        for i, msg in enumerate(messages):
            with st.chat_message(msg["role"]):
                st.markdown(f"**{msg['role'].capitalize()}** ({msg['formatted_time']}): {msg['content']}")

                # Action buttons
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("✏️ Edit", key=f"edit_{i}"):
                        st.session_state.edit_index = i
                        st.session_state.edit_content = msg["content"]
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{i}"):
                        from services.chat_service import delete_message
                        delete_message(i)
                        st.rerun()
    # Editing interface
    if "edit_index" in st.session_state:
        edit_index = st.session_state.edit_index
        new_content = st.text_area("Edit Message", value=st.session_state.edit_content, key="edit_content_area")

        if st.button("💾 Save Edit"):
            from services.chat_service import update_message
            update_message(edit_index, new_content)
            del st.session_state.edit_index
            del st.session_state.edit_content
            st.rerun()

        if st.button("❌ Cancel Edit"):
            del st.session_state.edit_index
            del st.session_state.edit_content
            st.rerun()
    
    if st.button("🧹 Clear Conversation"):
        reset_current_conversation()
        st.rerun()

    # File uploader near input (right before chat input)
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"], label_visibility="collapsed")
    if uploaded_file:
        # Here you'd call your own upload/save logic
        st.success(f"Uploaded: {uploaded_file.name}")
        # You might want to integrate something like: save_uploaded_file(uploaded_file)

    # Chat input
    user_input = st.chat_input("Type your message...")
    if user_input:
        handle_message(user_input, is_document_query=bool(docs or uploaded_file))
        st.rerun()
