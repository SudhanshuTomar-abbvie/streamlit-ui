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
    # Inject CSS to style buttons & fix input to bottom
    st.markdown(
        """
        <style>
        /* Make all baseweb buttons (used by st.button) smaller */
        button[data-baseweb="button"] {
            padding: 0.25rem 0.4rem !important;
            font-size: 0.75rem !important;
            line-height: 1 !important;
        }

        /* Fix the chat-input container to bottom */
        div[data-testid="stChatInput"] {
            position: fixed !important;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 0.5rem 1rem;
            background: var(--bg-color);
            box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
            z-index: 1000;
        }

        /* Give the main chat area extra bottom padding
           so messages never get hidden behind the fixed input */
        .stApp > div.block-container {
            padding-bottom: 5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Chat title
    current_title = st.session_state.current_conversation_title
    new_title = st.text_input("Chat Title", value=current_title, key="chat_title_input")
    if new_title != current_title:
        change_conversation_title(new_title)

    st.caption(f"🕓 Last updated: {datetime.now().strftime('%I:%M:%S %p')}")

    # Toggle doc uploader
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False

    if st.button("📌", key="toggle_uploader", help="Toggle Document Upload"):
        st.session_state.show_uploader = not st.session_state.show_uploader

    if st.session_state.show_uploader:
        uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
        if uploaded_file:
            processed_doc = process_uploaded_file(uploaded_file)
            if processed_doc:
                st.success(f"Uploaded: {processed_doc['name']}")
            else:
                st.error("Failed to process uploaded document")

    # Uploaded docs info
    docs = get_uploaded_documents()
    if docs:
        st.info(f"📄 {len(docs)} document{'s' if len(docs) > 1 else ''} uploaded")

    # Edit mode (optional external UI)
    is_editing = render_message_editor()

    if not is_editing:
        messages = get_formatted_messages()
        for i, msg in enumerate(messages):
            with st.chat_message(msg["role"]):
                st.markdown(f"**{msg['role'].capitalize()}** ({msg['formatted_time']}): {msg['content']}")

                # Compact edit/delete buttons
                col1, col2 = st.columns([0.08, 0.08])
                with col1:
                    if st.button("✏️", key=f"edit_{i}", help="Edit"):
                        st.session_state.edit_index = i
                        st.session_state.edit_content = msg["content"]
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"delete_{i}", help="Delete"):
                        delete_message(i)
                        st.rerun()

    # Edit form if in edit mode
    if "edit_index" in st.session_state:
        new_content = st.text_area("Edit Message", value=st.session_state.edit_content, key="edit_content_area")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save"):
                update_message(st.session_state.edit_index, new_content)
                del st.session_state.edit_index
                del st.session_state.edit_content
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                del st.session_state.edit_index
                del st.session_state.edit_content
                st.rerun()

    # Clear conversation
    if st.button("🧹 Clear Conversation"):
        reset_current_conversation()
        st.rerun()

    # Chat input (this will now stick to the bottom)
    user_input = st.chat_input("Type your message…")
    if user_input:
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "formatted_time": datetime.now().strftime("%I:%M %p"),
            "edited": False
        })
        st.rerun()

    # Render last user message and spinner while processing
    if st.session_state.get("messages"):
        last_message = st.session_state.messages[-1]
        if last_message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(f"**You** ({last_message['formatted_time']}): {last_message['content']}")
            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    handle_message(last_message["content"], is_document_query=bool(docs))
                    st.rerun()
