# import streamlit as st
# from services.chat_service import create_new_chat
# from ui.health_indicator import render_health_indicator

# def render_sidebar():
#     """Render the sidebar with chat history and health status"""
#     with st.sidebar:
#         st.title("MLOps Chatbot")
        
#         # New chat button
#         if st.button("New Chat", key="new_chat"):
#             create_new_chat()
#             st.rerun()
        
#         st.divider()
        
#         # List all conversations sorted by timestamp descending
#         render_chat_list()
        
#         st.divider()
        
#         # Display health status indicator
#         render_health_indicator()

# def render_chat_list():
#     """Render the list of chat conversations"""
#     st.subheader("Chat History")
    
#     for chat_id, chat_data in sorted(
#         st.session_state.conversations.items(),
#         key=lambda x: x[1]["timestamp"],
#         reverse=True
#     ):
#         if st.button(
#             chat_data["title"],
#             key=f"chat_{chat_id}",
#             use_container_width=True
#         ):
#             st.session_state.current_chat_id = chat_id
#             st.session_state.messages = chat_data["messages"]
#             st.rerun()


import streamlit as st
from services.chat_service import create_new_chat
from ui.health_indicator import render_health_indicator

def render_sidebar():
    """Styled sidebar"""
    with st.sidebar:
        st.markdown("### MLOps Chatbot")
        
        if st.button("➕ New Chat", key="new_chat"):
            create_new_chat()
            st.rerun()

        st.markdown("---")
        render_chat_list()
        st.markdown("---")
        render_health_indicator()

def render_chat_list():
    st.subheader("🕑 Chat History")

    for chat_id, chat_data in sorted(
        st.session_state.conversations.items(),
        key=lambda x: x[1]["timestamp"],
        reverse=True
    ):
        if st.button(chat_data["title"], key=f"chat_{chat_id}", use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.session_state.messages = chat_data["messages"]
            st.rerun()