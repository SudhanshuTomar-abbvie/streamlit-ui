# utils/constants.py

import os

# API endpoints
BACKEND_API_BASE_URL = "http://k8s-default-dkumadse-f38d97347b-066209af6eb01332.elb.us-east-1.amazonaws.com/public/api/v1"
API_ENDPOINT = f"{BACKEND_API_BASE_URL}/chat/retrieve/run"
DOCUMENT_QUERY_API_ENDPOINT = f"{BACKEND_API_BASE_URL}/chat/process_documents/run"
HEALTH_ENDPOINT = f"{BACKEND_API_BASE_URL}/chat/health/run"

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)  # Create data directory if it doesn't exist

HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")

# App constants
APP_TITLE = "MLOPS Chatbot"
APP_ICON = "🏥"
SIDEBAR_TITLE = "MLOPS Chatbot"
SIDEBAR_SUBTITLE = "Patient Touchpoint Knowledge Agent"

# Health check interval in seconds
HEALTH_CHECK_INTERVAL = 5