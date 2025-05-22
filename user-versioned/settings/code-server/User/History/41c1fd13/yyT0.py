import streamlit as st
import os

# Constants
BACKEND_API_BASE_URL = "http://k8s-default-dkumadse-f38d97347b-066209af6eb01332.elb.us-east-1.amazonaws.com/public/api/v1"
API_ENDPOINT = f"{BACKEND_API_BASE_URL}/chat/retrieve/run" #f"{BACKEND_API_BASE_URL}/chat/generate/run"
DOCUMENT_QUERY_API_ENDPOINT = f"{BACKEND_API_BASE_URL}/chat/process_documents/run"


# Private API
# BACKEND_API_BASE_URL = "https://cdl-dku-genai01.commercial-datalake-prod.awscloud.abbvienet.com/public/api/v1" 
# API_ENDPOINT = f"{BACKEND_API_BASE_URL}/mlopsChatbot/generate/run"
# DOCUMENT_QUERY_API_ENDPOINT = f"{BACKEND_API_BASE_URL}/mlopsChatbot/ChatOnDocument/run"


HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chat_history.json")

# Allowed document file types
ALLOWED_DOCUMENT_TYPES = ["pdf", "docx", "txt", "csv", "json", "md"]

# def setup_page_config():
#     """Configure Streamlit page settings"""
#     st.set_page_config(
#         page_title="MLOps Chatbot",
#         page_icon="💬",
#         layout="wide"
#     )

import streamlit as st

def setup_page_config():
    st.set_page_config(
        page_title="MLOps Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS for consistent UI styling
    st.markdown("""
        <style>
            html, body, [class*="css"]  {
                font-family: 'Segoe UI', sans-serif;
                background-color: #F0F2F6;
            }
            .stButton>button {
                background-color: #1F4E79;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.5em 1em;
                font-weight: 600;
            }
            .stTextInput>div>div>input {
                border-radius: 8px;
                padding: 0.5em;
            }
            .stChatInputContainer {
                background: white;
                border-radius: 8px;
                padding: 1em;
                box-shadow: 0 0 6px rgba(0,0,0,0.1);
            }
        </style>
    """, unsafe_allow_html=True)