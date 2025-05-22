import streamlit as st
import os
from utils.rendering import render_svg
import logging
from services.health_service import get_health_status

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_sidebar():
    """
    Render the application sidebar with navigation and status
    """
    with st.sidebar:
        # Logo
        st.sidebar.image("assets/abbvielogo.png")
        
        # Title and subtitle
        st.markdown('<div class="sidebar-title">MLOPS Chatbot</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-subtitle">Patient Touchpoint Knowledge Agent</div>', unsafe_allow_html=True)
        
        # Navigation buttons
        if st.button("🏠 Home", key="nav_home"):
            st.session_state.current_page = "home"
            st.rerun()
        
        if st.button("💬 Chat", key="nav_chat"):
            st.session_state.current_page = "chat"
            st.rerun()

        if st.button("📡 Upload Docs", key="nav_history"):
            st.session_state.current_page = "ukb"
            st.rerun()
        
        if st.button("📊 Conversation History", key="nav_history"):
            st.session_state.current_page = "conversation_history"
            st.rerun()
        
        if st.button("ℹ️ Information", key="nav_info"):
            st.session_state.current_page = "information"
            st.rerun()
        
        # Health status indicator
        health_status = get_health_status()
        status_class = "healthy" if health_status else "unhealthy"
        status_text = "System Online" if health_status else "System Offline"
        
        st.markdown(
            f'<div class="health-indicator"><div class="health-status {status_class}"></div>{status_text}</div>',
            unsafe_allow_html=True
        )
        
        # User info at bottom
        st.markdown(
            f'<div class="user-info">{st.session_state.user_info["name"]}<br><a href="#" style="color: white; text-decoration: none;">Logout</a></div>',
            unsafe_allow_html=True
        )