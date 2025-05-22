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
    # 1) Inject CSS to fix z-indexes and layout
    st.markdown("""
        <style>
        /* make chat‐input container truly fixed & above sidebar */
        div[data-testid="stChatInput"] {
            position: fixed !important;
            bottom: 0; left: 0; right: 0;
            z-index: 1002;  /* above most things */
            background: var(--bg-color);
            padding: 0.5rem 1rem;
            box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
        }
        /* push page content up so it never goes beneath the fixed input */
        .stApp > .main > div.block-container {
            padding-bottom: 5rem !important;
        }
        /* small button style */
        button[data-baseweb="button"] {
            padding: 0.25rem 0.4rem !important;
            font-size: 0.75rem !important;
            line-height: 1 !important;
        }
        /* Footer area for “powered by” */
        .powered-by {
            position: fixed;
            bottom: 2.5rem; /* just above the input */
            left: 0; right: 0;
            text-align: center;
            font-size: 0.8rem;
            color: var(--secondary-text-color);
            z-index: 1001;
        }
        </style>
    """, unsafe_allow_html=True)

    # Chat title & timestamp
    current_title = st.session_state.current_conversation_title
    new_title = st.text_input("Chat Title", value=current_title, key="chat_title_input")
    if new_title != current_title:
        change_conversation_title(new_title)
    st.caption(f"🕓 Last updated: {datetime.now().strftime('%I:%M:%S %p')}")

    # Uploader state
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False

    # Show/hide uploader panel up here if desired
    if st.session_state.show_uploader:
        uploaded_file = st.file_uploader("Upload a document", type=["pdf","docx","txt"])
        if uploaded_file:
            processed = process_uploaded_file(uploaded_file)
            if processed:
                st.success(f"Uploaded: {processed['name']}")
            else:
                st.error("Failed to process uploaded document")

    # Info on uploaded docs
    docs = get_uploaded_documents()
    if docs:
        st.info(f"📄 {len(docs)} doc{'s' if len(docs)>1 else ''} uploaded")

    # Render editor mode if active
    is_editing = render_message_editor()

    if not is_editing:
        for i, msg in enumerate(get_formatted_messages()):
            with st.chat_message(msg["role"]):
                st.markdown(f"**{msg['role'].capitalize()}** ({msg['formatted_time']}): {msg['content']}")
                # compact edit/delete
                c1,c2 = st.columns([0.08,0.08])
                with c1:
                    if st.button("✏️", key=f"edit_{i}", help="Edit"):
                        st.session_state.edit_index = i
                        st.session_state.edit_content = msg["content"]
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_{i}", help="Delete"):
                        delete_message(i)
                        st.rerun()

    # In‐place edit form
    if "edit_index" in st.session_state:
        new_txt = st.text_area("Edit Message", value=st.session_state.edit_content)
        s,c = st.columns(2)
        with s:
            if st.button("💾 Save"):
                update_message(st.session_state.edit_index, new_txt)
                del st.session_state.edit_index
                del st.session_state.edit_content
                st.rerun()
        with c:
            if st.button("❌ Cancel"):
                del st.session_state.edit_index
                del st.session_state.edit_content
                st.rerun()

    # Clear conversation
    if st.button("🧹 Clear Conversation"):
        reset_current_conversation()
        st.rerun()

    # 2) Build a two‐column row that sits *inside* the fixed input bar
    with st.container():
        col_pin, col_input = st.columns([0.08, 0.92], gap="small")
        with col_pin:
            # pin icon toggles the uploader
            if st.button("📌", key="pin_upload", help="Toggle Document Upload"):
                st.session_state.show_uploader = not st.session_state.show_uploader
        with col_input:
            user_input = st.chat_input("Type your message…")

    # 3) Handle user submission
    if user_input:
        # you already push to session_state.messages inside handle_message
        handle_message(user_input, is_document_query=bool(docs))
        st.rerun()

    # 4) “Powered by MLOPS” footer
    st.markdown('<div class="powered-by">Powered by MLOPS Chatbot</div>', unsafe_allow_html=True)
