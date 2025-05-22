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

def _on_send():
    """
    Callback for Send button:
    1) grab the text_input value,
    2) stash it in temp_user_input,
    3) clear the widget’s session_state key.
    """
    txt = st.session_state.user_input_text
    if not txt:
        return
    st.session_state.temp_user_input = txt
    st.session_state.user_input_text = ""
    # NO st.rerun() here!

def render_chat_page():
    # --- Custom CSS ---
    st.markdown("""
        <style>
        .main .block-container { padding-top: 1rem; padding-bottom: 0; max-width: 80%vw; }
        .stChatFloatingInputContainer { display: none !important; }
        .chat-header { position: sticky; top: 0; background-color: white; z-index: 100;
                       padding-bottom: 1rem; border-bottom: 1px solid #f0f0f0; }
        .chat-messages { margin-bottom: 6rem; padding-bottom: 1rem; min-height: 70%vh; }
        .chat-input-container { position: fixed; bottom: 2px; background-color: white;
                                 padding: 10px 1rem; z-index: 100; border-top: 1px solid #f0f0f0; }
        .chat-footer { position: fixed; bottom: 0; left: 0; right: 0; height: 10px;
                       background-color: white; z-index: 99; padding: 10px 1rem;
                       text-align: center; font-size: 0.8rem; color: gray;
                       border-top: 1px solid #f0f0f0; }
        .edit-buttons { visibility: visible; opacity: 0.6; }
        .edit-buttons:hover { opacity: 1; }
        .stChatMessage { margin-bottom: 1rem; }
        </style>
    """, unsafe_allow_html=True)

    # SECTION 1: HEADER
    with st.container():
        st.markdown('<div class="chat-header">', unsafe_allow_html=True)
        current_title = st.session_state.current_conversation_title
        new_title = st.text_input("Chat Title", value=current_title, key="chat_title_input")
        if new_title != current_title:
            change_conversation_title(new_title)
        st.caption(f"🕓 Last updated: {datetime.now().strftime('%I:%M:%S %p')}")

        docs = get_uploaded_documents()
        if docs:
            st.info(f"📄 {len(docs)} document{'s' if len(docs)>1 else ''} uploaded")

        if "show_uploader" not in st.session_state:
            st.session_state.show_uploader = False
        if st.session_state.show_uploader:
            uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
            if uploaded_file:
                processed = process_uploaded_file(uploaded_file)
                if processed:
                    st.success(f"Uploaded: {processed['name']}")
                    st.session_state.show_uploader = False
                    st.rerun()
                else:
                    st.error("Failed to process uploaded document")
        st.markdown('</div>', unsafe_allow_html=True)

    # SECTION 2: MESSAGE HISTORY
    with st.container():
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

        # --- Check if message was sent from another page (like Home) ---
        if st.session_state.get("pending_user_input"):
            st.session_state.temp_user_input = st.session_state.pending_user_input
            del st.session_state.pending_user_input

        is_editing = render_message_editor()
        if not is_editing:
            for i, msg in enumerate(get_formatted_messages()):
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    col1, col2, col3 = st.columns([0.94, 0.03, 0.03])
                    with col2:
                        if st.button("✏️", key=f"edit_{i}", help="Edit"):
                            st.session_state.edit_index = i
                            st.session_state.edit_content = msg["content"]
                            st.rerun()
                    with col3:
                        if st.button("🗑️", key=f"del_{i}", help="Delete"):
                            delete_message(i)
                            st.rerun()

        if "edit_index" in st.session_state:
            with st.container():
                new_txt = st.text_area("Edit Message", value=st.session_state.edit_content, height=100)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💾 Save"):
                        update_message(st.session_state.edit_index, new_txt)
                        del st.session_state.edit_index
                        del st.session_state.edit_content
                        st.rerun()
                with c2:
                    if st.button("❌ Cancel"):
                        del st.session_state.edit_index
                        del st.session_state.edit_content
                        st.rerun()

        # --- Process the queued user message (from input or home screen) ---
        if st.session_state.get("temp_user_input"):
            user_input = st.session_state.temp_user_input
            st.session_state.temp_user_input = None

            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Pondering..."):
                    handle_message(user_input, is_document_query=bool(docs))

            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # SECTION 3: INPUT AREA (fixed at bottom), no form
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    col_attach, col_input = st.columns([0.08, 0.92])

    with col_attach:
        if st.button("📎", key="toggle_upload"):
            st.session_state.show_uploader = not st.session_state.show_uploader
            st.rerun()

    with col_input:
        if "user_input_text" not in st.session_state:
            st.session_state.user_input_text = ""
        st.text_input(
            "Type your message…",
            key="user_input_text",
            label_visibility="collapsed",
            placeholder="Type your message here"
        )
        st.button("Send", key="send_message", on_click=_on_send)

    st.markdown('</div>', unsafe_allow_html=True)
