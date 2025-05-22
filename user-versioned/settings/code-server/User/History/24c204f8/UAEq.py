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
    """
    Render the chat interface with a three-part layout, responsive to screen size:
    1. Header section (title, document info)
    2. Message history (scrollable area with all messages)
    3. Input section (fixed at bottom with input, document toggle, and footer)
    """
    # Apply custom CSS with responsive design
    st.markdown("""
        <style>
        /* Remove default Streamlit padding and spacing */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 0;
            max-width: 100%;
        }
        
        /* Hide the default floating chat input */
        .stChatFloatingInputContainer {
            display: none !important;
        }
        
        /* Fixed header area */
        .chat-header {
            position: sticky;
            top: 0;
            background-color: white;
            z-index: 100;
            padding-bottom: 1rem;
            border-bottom: 1px solid #f0f0f0;
        }
        
        /* Messages area with responsive spacing */
        .chat-messages {
            margin-bottom: 120px;  /* Base space for input area */
            padding-bottom: 1rem;
            min-height: 200px;
        }
        
        /* Fixed input area at bottom with responsive height */
        .chat-input-container {
            position: fixed;
            bottom: 40px;  /* Space for footer */
            left: 0;
            right: 0;
            background-color: white;
            padding: 10px 1rem;
            z-index: 100;
            border-top: 1px solid #f0f0f0;
        }
        
        /* Footer at bottom */
        .chat-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 40px;
            background-color: white;
            z-index: 99;
            padding: 10px 1rem;
            text-align: center;
            font-size: 0.8rem;
            color: gray;
            border-top: 1px solid #f0f0f0;
        }
        
        /* Message styling */
        .edit-buttons {
            visibility: visible;
            opacity: 0.6;
        }
        .edit-buttons:hover {
            opacity: 1;
        }

        /* Ensuring message spacing */
        .stChatMessage {
            margin-bottom: 1rem;
        }
        
        /* Responsive settings */
        @media (max-width: 768px) {
            .chat-messages {
                margin-bottom: 140px;  /* More space on small screens */
            }
            
            .message-buttons {
                display: flex;
                justify-content: flex-end;
            }
        }
        
        @media (min-width: 1200px) {
            .chat-container {
                max-width: 80%;
                margin: 0 auto;
            }
        }
        
        /* More generous spacing on larger screens */
        @media (min-width: 992px) {
            .chat-message-content {
                padding: 0.5rem 1rem;
            }
        }
        
        /* Give more space to the text input */
        .input-text {
            padding: 0.5rem 0;
        }
        
        /* Submit button styling */
        .submit-button {
            margin-top: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Main chat container with responsive width
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # SECTION 1: HEADER
    # -----------------
    with st.container():
        st.markdown('<div class="chat-header">', unsafe_allow_html=True)
        
        # Chat title input
        current_title = st.session_state.current_conversation_title
        new_title = st.text_input("Chat Title", value=current_title, key="chat_title_input")
        if new_title != current_title:
            change_conversation_title(new_title)
        
        st.caption(f"🕓 Last updated: {datetime.now().strftime('%I:%M:%S %p')}")
        
        # Show info about uploaded documents
        docs = get_uploaded_documents()
        if docs:
            st.info(f"📄 {len(docs)} document{'s' if len(docs)>1 else ''} uploaded")
            
        # Document upload section (toggled by attachment button)
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
    # --------------------------
    with st.container():
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        
        # Check if we're in edit mode
        is_editing = render_message_editor()
        
        # Display message history
        if not is_editing:
            # Get all messages
            messages = get_formatted_messages()
            
            # Display each message
            for i, msg in enumerate(messages):
                with st.chat_message(msg["role"]):
                    st.markdown(f'<div class="chat-message-content">{msg["content"]}</div>', unsafe_allow_html=True)
                    
                    # Edit/delete buttons with responsive layout
                    with st.container():
                        st.markdown('<div class="message-buttons">', unsafe_allow_html=True)
                        col1, col2 = st.columns([0.97, 0.03])
                        with col2:
                            # Use columns for the buttons
                            button_cols = st.columns([1, 1])
                            with button_cols[0]:
                                if st.button("✏️", key=f"edit_{i}", help="Edit"):
                                    st.session_state.edit_index = i
                                    st.session_state.edit_content = msg["content"]
                                    st.rerun()
                            with button_cols[1]:
                                if st.button("🗑️", key=f"del_{i}", help="Delete"):
                                    delete_message(i)
                                    st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
        
        # In-place edit form when editing a message
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
        
        # Process new user message if we have one in the session state
        if "new_user_message" in st.session_state and st.session_state.new_user_message:
            user_input = st.session_state.new_user_message
            st.session_state.new_user_message = ""  # Clear it immediately
            
            # Add user message to display
            with st.chat_message("user"):
                st.markdown(f'<div class="chat-message-content">{user_input}</div>', unsafe_allow_html=True)
                
            # Show AI thinking with spinner
            with st.chat_message("assistant"):
                with st.spinner("Pondering..."):
                    # Process the message
                    handle_message(user_input, is_document_query=bool(docs))
                    st.rerun()
                    
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SECTION 3: INPUT AREA (fixed at bottom)
    # ---------------------------------------
    # The input container (fixed position)
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    
    # We'll use a form to handle the input submission properly
    with st.form(key="chat_input_form"):
        # Create custom input area with columns - responsive layout
        input_cols = st.columns([0.08, 0.92])
        
        # Document upload toggle button
        with input_cols[0]:
            upload_toggle = st.form_submit_button("📎", help="Upload document")
        
        # Text input area
        with input_cols[1]:
            user_msg = st.text_input(
                "Type your message...", 
                key="user_msg_input",
                label_visibility="collapsed",
                placeholder="Type your message..."
            )
            
        # Submit button - centered and below input for better visibility
        submit_button = st.form_submit_button("Send", use_container_width=True)
        
        # Handle form submission
        if submit_button and user_msg:
            st.session_state.new_user_message = user_msg
            st.rerun()
    
    # Handle document upload toggle separately since it's in a form
    if "upload_toggle" in locals() and upload_toggle:
        st.session_state.show_uploader = not st.session_state.show_uploader
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="chat-footer">Powered by MLOPS Chatbot</div>', unsafe_allow_html=True)
    
    # Close the main container
    st.markdown('</div>', unsafe_allow_html=True)