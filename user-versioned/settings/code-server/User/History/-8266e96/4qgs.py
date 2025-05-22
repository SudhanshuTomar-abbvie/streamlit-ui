# import streamlit as st
# from ui.components import render_message, render_document_upload
# from services.chat_service import process_user_input, toggle_document_upload

# def render_main_panel():
#     """Render the main chat interface"""
#     st.title("MLOps Chatbot")
    
#     # Create a container for messages that will scroll
#     chat_container = st.container()
    
#     # Create a static container at the bottom for input
#     input_container = st.container()
    
#     # First render the input area (at the bottom of the page)
#     with input_container:
#         # Document upload panel (if toggled on)
#         if st.session_state.show_document_upload:
#             render_document_upload()
        
#         # User input handling
#         render_chat_input()
    
#     # Then render messages (which will appear above the input)
#     with chat_container:
#         render_chat_messages()

# def render_chat_messages():
#     """Render all chat messages in the conversation"""
#     for i, message in enumerate(st.session_state.messages):
#         render_message(message, i)

# def render_chat_input():
#     """Render the chat input field with document upload button"""
#     # Button to toggle document upload
#     col1, col2 = st.columns([12, 1])
    
#     with col1:
#         # Chat input field
#         prompt = st.chat_input(
#             "Ask something..." if not st.session_state.uploaded_documents else 
#             f"Ask about the {len(st.session_state.uploaded_documents)} uploaded document(s)..."
#         )
    
#     with col2:
#         # Document pin button (positioned near the input field)
#         document_button = st.button(
#             "📎" if not st.session_state.show_document_upload else "❌", 
#             key="toggle_document_upload",
#             help="Upload documents to query" if not st.session_state.show_document_upload else "Close document upload"
#         )
#         if document_button:
#             toggle_document_upload()
#             st.rerun()
    
#     # Indicator for uploaded documents
#     if st.session_state.uploaded_documents:
#         st.caption(f"📎 {len(st.session_state.uploaded_documents)} document(s) ready")
    
#     # Process user input if provided
#     if prompt:
#         # Process user input and get response
#         with st.spinner("Thinking..."):
#             response_text = process_user_input(prompt)
            
#         # Rerun to refresh the UI (this will redraw everything)
#         st.rerun()


import streamlit as st
from ui.components import render_message, render_document_upload
from services.chat_service import process_user_input, toggle_document_upload

def render_main_panel():
    """Render the main chat interface"""
    st.markdown("## MLOps Chatbot", unsafe_allow_html=True)

    # Chat container
    chat_container = st.container()
    input_container = st.container()

    # Chat messages
    with chat_container:
        render_chat_messages()

    # Chat input and doc upload
    with input_container:
        render_chat_input()

def render_chat_messages():
    """Render all chat messages"""
    for i, message in enumerate(st.session_state.messages):
        render_message(message, i)

def render_chat_input():
    """Chat input with document upload toggle"""
    col1, col2 = st.columns([12, 1])

    with col1:
        prompt = st.chat_input(
            "Ask your MLOps question..." if not st.session_state.uploaded_documents else 
            f"Ask about the {len(st.session_state.uploaded_documents)} uploaded document(s)..."
        )

    with col2:
        toggle_label = "📎" if not st.session_state.show_document_upload else "❌"
        document_button = st.button(
            toggle_label,
            key="toggle_document_upload",
            help="Upload documents to query" if not st.session_state.show_document_upload else "Close upload"
        )
        if document_button:
            toggle_document_upload()
            st.rerun()

    if st.session_state.show_document_upload:
        with st.expander("📎 Upload Documents", expanded=True):
            render_document_upload()

    if st.session_state.uploaded_documents:
        st.caption(f"📎 {len(st.session_state.uploaded_documents)} document(s) uploaded")

    if prompt:
        with st.spinner("Thinking..."):
            response = process_user_input(prompt)
        st.rerun()