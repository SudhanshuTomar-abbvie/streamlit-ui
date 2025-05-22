# Modified chat_page.py
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
    # --- Custom CSS ---
    st.markdown("""
        <style>
        .main .block-container { padding-top: 1rem; padding-bottom: 0; }
        .stChatFloatingInputContainer { display: none !important; }
        .chat-header { position: sticky; top: 0; background-color: white; z-index: 100;
                      padding-bottom: 1rem; border-bottom: 1px solid #f0f0f0; }
        .chat-messages { margin-bottom: 6rem; padding-bottom: 1rem; min-height: 70vh; }
        .chat-input-container { position: fixed; bottom: 2px; background-color: white;
                              padding: 10px 1rem; z-index: 100; border-top: 1px solid #f0f0f0; }
        .context-expander { margin-top: 1rem; border: 1px solid #f0f0f0; border-radius: 4px; }
        .upload-container { margin-bottom: 1rem; }
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

        
        st.markdown('</div>', unsafe_allow_html=True)

    # SECTION 2: MESSAGE HISTORY
    with st.container():
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

        # Check if message was sent from another page (like Home)
        if st.session_state.get("pending_user_input"):
            st.session_state.temp_user_input = st.session_state.pending_user_input
            del st.session_state.pending_user_input

        is_editing = render_message_editor()
        if not is_editing:
            for i, msg in enumerate(get_formatted_messages()):
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
                    # Add context expander if it exists in the message
                    if "context" in msg and msg["context"]:
                        with st.expander("View retrieved context"):
                            st.markdown(msg["context"])
                    
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

        # Process the queued user message
        if st.session_state.get("temp_user_input"):
            user_input = st.session_state.temp_user_input
            st.session_state.temp_user_input = None

            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    handle_message(user_input, is_document_query=bool(docs))

            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # SECTION 3: INPUT AREA (fixed at bottom with integrated pin)
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    
    # Custom input with integrated pin
    cols = st.columns([0.05, 0.95])
    
    with cols[0]:
        if st.button("📎", key="pin_button"):
            st.session_state.show_uploader = not st.session_state.get("show_uploader", False)
            st.rerun()
            
    with cols[1]:
        # Initialize the session state variable for the input text if not exists
        if "user_input_text" not in st.session_state:
            st.session_state.user_input_text = ""
            
        # Function to process when Enter is pressed
        def handle_enter():
            if st.session_state.user_input_text.strip():
                st.session_state.temp_user_input = st.session_state.user_input_text
                st.session_state.user_input_text = ""
                st.rerun()
                
        # Text input that captures Enter key
        user_input = st.text_input(
            "Type your message…",
            key="user_input_text",
            on_change=handle_enter,
            label_visibility="collapsed",
            placeholder="Type your message here and press Enter"
        )

    st.markdown('</div>', unsafe_allow_html=True)