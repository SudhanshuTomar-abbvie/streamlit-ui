
import streamlit as st
from services.chat_service import handle_message
from utils.rendering import render_svg
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_home_page():
    """
    Render the home page with welcome message and quick access features
    """
    # Prevent UI flicker when transitioning to chat
    if st.session_state.get("current_page") != "home":
        return
    # Get SVG content for logo
    img_content = render_svg("assets/avatarlogo.svg")
    
    st.markdown('<div class="welcome-container">', unsafe_allow_html=True)
    
    # Welcome header with logo
    st.markdown('<h1 style="text-align:center !important;" class="welcome-title">Welcome to PATOKA Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center !important;" class="welcome-subtitle">Patient Touchpoint Knowledge Agent</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center !important;" >A generative AI chatbot designed to provide insights about patient touchpoints and healthcare experiences.</p>', unsafe_allow_html=True)
    
    # Search input field
    st.markdown('<div class="centered-container">', unsafe_allow_html=True)
    
    # Function to process when Enter is pressed
    def handle_enter():
        user_input_val = st.session_state.get("home_input", "")
        if user_input_val:
            st.session_state.pending_user_input = user_input_val
            st.session_state.current_page = "chat"
            # st.rerun()

    # Text input with default value
    user_input = st.text_input(
        label="home_chat_input",
        placeholder="Ask any question...",
        on_change=handle_enter,
        key="home_input",
        label_visibility="collapsed"
    )
    
    # Button
    if st.button("Ask and Go to Chat", key="home_ask_button"):
        if user_input:
            st.session_state.pending_user_input = user_input  # Stash for later
            st.session_state.current_page = "chat"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Popular questions
    st.markdown('<h2 style="text-align:center; margin-top:40px;">Popular Questions</h2>', unsafe_allow_html=True)
    
    popular_questions = [
        "What are common patient complaints during discharge?",
        "How can we improve ER wait times?",
        "What factors most impact patient satisfaction?",
        "How do patients prefer to receive follow-up information?"
    ]
    
    # Arrange popular questions in 2 columns
    cols = st.columns(2)
    for i, question in enumerate(popular_questions):
        with cols[i % 2]:
            if st.button(question, key=f"popular_q_{i}"):
                handle_message(question)
                st.session_state.current_page = "chat"
                st.rerun()
    
    # Feature showcase section (optional)
    st.markdown('<h2 style="text-align:center; margin-top:40px;">Key Features</h2>', unsafe_allow_html=True)
    
    feature_cols = st.columns(3)
    
    with feature_cols[0]:
        st.markdown("""
        ### 💬 Chat with AI
        Ask questions about patient touchpoints and healthcare experiences.
        """)
    
    with feature_cols[1]:
        st.markdown("""
        ### 📄 Document Analysis
        Upload documents to analyze patient feedback and data.
        """)
    
    with feature_cols[2]:
        st.markdown("""
        ### 🔍 Insights
        Get actionable insights from patient data.
        """)