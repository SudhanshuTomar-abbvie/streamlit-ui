import streamlit as st
from datetime import datetime
from components import render_message, render_document_upload
from services.chat_service import process_user_input, toggle_document_upload
from utils.session_state import reset_current_conversation


def render_main_panel():
    """Render the main chat interface"""
    st.markdown("## 🧠 MLOps Assistant", unsafe_allow_html=True)

    # Container structure
    chat_container = st.container()
    input_container = st.container()

    # Chat messages first (scrolling section)
    with chat_container:
        render_chat_messages()

    # Input field + doc toggle (bottom fixed area)
    with input_container:
        render_chat_input()


def render_chat_messages():
    """Render chat messages from session"""
    for i, message in enumerate(st.session_state.get("messages", [])):
        render_message(message, i)


def render_chat_input():
    """Chat input with doc pin toggle, document uploader, and spinner"""

    # Layout: Input box + 📎 toggle button
    col1, col2 = st.columns([12, 1])

    with col1:
        prompt = st.chat_input(
            "Type your question..." if not st.session_state.uploaded_documents else
            f"Ask about {len(st.session_state.uploaded_documents)} uploaded document(s)..."
        )

    with col2:
        pin_label = "📎" if not st.session_state.show_document_upload else "❌"
        if st.button(pin_label, key="toggle_document_upload", help="Toggle document upload"):
            toggle_document_upload()
            st.rerun()

    # Show document upload if toggled
    if st.session_state.show_document_upload:
        with st.expander("📎 Upload Documents", expanded=True):
            render_document_upload()

    if st.session_state.uploaded_documents:
        st.caption(f"📄 {len(st.session_state.uploaded_documents)} document(s) uploaded")

    # On prompt submit: show user message + spinner + response
    if prompt:
        # Save user input as message (before processing)
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "formatted_time": datetime.now().strftime("%I:%M %p"),
            "edited": False
        })

        # Display spinner while generating response
        with st.spinner("Thinking..."):
            response_text = process_user_input(prompt)

        # Save assistant's reply
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "formatted_time": datetime.now().strftime("%I:%M %p"),
            "edited": False
        })

        # Trigger full rerun (keeps layout, shows latest messages)
        st.rerun()
