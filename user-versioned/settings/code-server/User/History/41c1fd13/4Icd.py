import streamlit as st
import os

# Constants
BACKEND_API_BASE_URL = "https://cdl-dku-genai01.commercial-datalake-prod.awscloud.abbvienet.com/public/api/v1/mlopsChatbot/generate/run" 
# BACKEND_API_BASE_URL = "http://k8s-default-dkumadse-f38d97347b-066209af6eb01332.elb.us-east-1.amazonaws.com:80/public/api/v1"
API_ENDPOINT = f"{BACKEND_API_BASE_URL}/chat/generate/run"
DOCUMENT_PROCESS_API_ENDPOINT = f"{BACKEND_API_BASE_URL}/chat/process_document/run"
HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chat_history.json")

# Allowed document file types
ALLOWED_DOCUMENT_TYPES = ["pdf", "docx", "txt", "csv", "json", "md"]

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="MLOps Chatbot",
        page_icon="💬",
        layout="wide"
    )