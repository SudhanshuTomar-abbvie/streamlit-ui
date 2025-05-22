import streamlit as st
from services.chat_service import start_edit_message, save_edited_message, cancel_edit, delete_message, save_feedback

# def render_message(message, index):
#     """
#     Render a chat message with options
    
#     Args:
#         message (dict): Message data
#         index (int): Message index
#     """
#     message_id = f"{st.session_state.current_chat_id}_{index}"
    
#     # Check if this message is being edited
#     if st.session_state.editing_message_index == index:
#         render_edit_interface(index)
#     else:
#         # Show regular message with options
#         with st.chat_message(message["role"]):
#             # Display document info if present
#             if message["role"] == "user" and "documents" in message and message["documents"]:
#                 render_document_info(message["documents"])
            
#             # Display message content
#             st.markdown(message["content"])
            
#             # Only show edit/delete options for user messages
#             if message["role"] == "user":
#                 render_user_message_options(index, message, message_id)
            
#             # Show feedback options for assistant messages
#             if message["role"] == "assistant" and index > 0:
#                 render_feedback_options(index)

import streamlit as st

def render_message(message, index):
    role = message.get("role", "")
    content = message.get("content", "")

    if role == "user":
        st.markdown(f"""
            <div style='background-color:#D6EAF8;padding:10px;border-radius:8px;margin:5px 0'>
                <b>You:</b><br>{content}
            </div>
        """, unsafe_allow_html=True)
    elif role == "assistant":
        st.markdown(f"""
            <div style='background-color:#F9E79F;padding:10px;border-radius:8px;margin:5px 0'>
                <b>Bot:</b><br>{content}
            </div>
        """, unsafe_allow_html=True)

def render_document_info(document_names):
    """
    Render information about documents attached to a message
    
    Args:
        document_names (list): List of document filenames
    """
    if document_names:
        with st.container():
            st.caption(f"📎 Documents: {', '.join(document_names)}")
            st.divider()

def render_edit_interface(index):
    """
    Render interface for editing a message
    
    Args:
        index (int): Message index being edited
    """
    with st.container():
        st.text_area("Edit message", key="edit_text_area", value=st.session_state.editing_text, 
                     on_change=lambda: setattr(st.session_state, "editing_text", st.session_state.edit_text_area))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", key=f"save_edit_{index}"):
                save_edited_message()
                st.rerun()
        with col2:
            if st.button("Cancel", key=f"cancel_edit_{index}"):
                cancel_edit()
                st.rerun()

def render_user_message_options(index, message, message_id):
    """
    Render options for user messages (edit, delete, context)
    
    Args:
        index (int): Message index
        message (dict): Message data
        message_id (str): Unique message ID
    """
    col1, col2, col3 = st.columns([1, 1, 5])
    with col1:
        if st.button("✏️ Edit", key=f"edit_{index}"):
            start_edit_message(index)
            st.rerun()
    with col2:
        if st.button("🗑️ Delete", key=f"delete_{index}"):
            delete_message(index)
            st.rerun()
    
    # Show context dropdown if available
    render_context_dropdown(message, message_id)

def render_context_dropdown(message, message_id):
    """
    Render dropdown for context information
    
    Args:
        message (dict): Message data
        message_id (str): Unique message ID
    """
    # First check if context exists directly in the message
    if "context" in message and message["context"]:
        context_data = message["context"]
    # Otherwise check the session state
    elif message_id in st.session_state.context and st.session_state.context[message_id]:
        context_data = st.session_state.context[message_id]
    else:
        # No context found
        return
    
    # Only display the expander if we have context data
    if context_data:
        with st.expander("Show retrieved context"):
            # if context_data is a string, display it directly
            if isinstance(context_data, str):
                st.markdown(context_data)
            # if it's a list, iterate over each item
            elif isinstance(context_data, list):
                for ctx_item in context_data:
                    if isinstance(ctx_item, dict):
                        st.markdown(f"**Source**: {ctx_item.get('source', 'Unknown')}")
                        st.markdown(ctx_item.get('text', 'No content available'))
                    else:
                        st.markdown(str(ctx_item))
                    st.divider()
            # If it's neither a string nor a list, simply display it
            else:
                st.markdown(str(context_data))

def render_feedback_options(index):
    """
    Render feedback options for assistant messages
    
    Args:
        index (int): Message index
    """
    # Get the associated user message index
    user_msg_idx = index - 1
    user_message_id = f"{st.session_state.current_chat_id}_{user_msg_idx}"
    
    # Check if feedback already given
    current_feedback = st.session_state.feedback.get(user_message_id, None)
    
    if current_feedback == "👍":
        st.markdown("You rated this response as helpful")
    elif current_feedback == "👎":
        st.markdown("You rated this response as not helpful")
    else:
        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            if st.button("👍", key=f"feedback_good_{index}"):
                save_feedback(user_msg_idx, "👍")
                st.rerun()
        with col2:
            if st.button("👎", key=f"feedback_bad_{index}"):
                save_feedback(user_msg_idx, "👎")
                st.rerun()

def render_document_upload():
    """Render document upload interface"""
    from config.settings import ALLOWED_DOCUMENT_TYPES
    
    st.markdown("### 📎 Upload Documents")
    
    # File uploader for documents
    uploaded_files = st.file_uploader(
        "Upload documents to query",
        type=ALLOWED_DOCUMENT_TYPES,
        accept_multiple_files=True,
        key="document_uploader"
    )
    
    # Display uploaded files and store them
    if uploaded_files:
        st.session_state.uploaded_documents = uploaded_files
        st.success(f"{len(uploaded_files)} document(s) uploaded successfully")
        
        # Display file information
        for file in uploaded_files:
            st.text(f"📄 {file.name} ({file.type}, {file.size} bytes)")
        
        # Clear button
        if st.button("Clear Documents", key="clear_documents"):
            from services.chat_service import clear_uploaded_documents
            clear_uploaded_documents()
            st.rerun()
    
    st.caption("Your documents will be sent along with your next message")