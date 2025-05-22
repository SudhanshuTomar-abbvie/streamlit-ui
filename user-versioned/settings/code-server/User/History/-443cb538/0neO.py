import streamlit as st
from config.settings import setup_page_config
from ui.sidebar import render_sidebar
from ui.main_panel import render_main_panel
from services.chat_service import initialize_chat_state
from utils.logging_utils import setup_logging

def main():
    # Setup logging
    setup_logging()
    
    # Configure page settings
    setup_page_config()
    
    # Initialize session state
    initialize_chat_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main panel
    render_main_panel()
    # realtime_qna()