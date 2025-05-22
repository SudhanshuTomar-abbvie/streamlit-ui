#constants.py
import os
from pathlib import Path
# API endpoints
BACKEND_API_BASE_URL = "http://10.242.92.241:10000/web-apps-backends/GENAIPOC/LmdRX0E" #"http://k8s-default-dkumadse-f38d97347b-066209af6eb01332.elb.us-east-1.amazonaws.com:80/public/api/v1"
# API_ENDPOINT = f"{BACKEND_API_BASE_URL}/chat/retrieve/run"
# DOCUMENT_QUERY_API_ENDPOINT = f"{BACKEND_API_BASE_URL}/chat/process_documents/run"
# HEALTH_ENDPOINT = "http://10.242.92.241:10000/web-apps-backends/GENAIPOC/LmdRX0E/query" #f"{BACKEND_API_BASE_URL}/chat/health/run"

API_ENDPOINT = f"{BACKEND_API_BASE_URL}/query"
DOCUMENT_QUERY_API_ENDPOINT = f"{BACKEND_API_BASE_URL}/query_on_doc"
HEALTH_ENDPOINT = f"{BACKEND_API_BASE_URL}/health"
UPDATE_KNOWLEDGE_BANK = f"{BACKEND_API_BASE_URL}/update_kb"
# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)  # Create data directory if it doesn't exist

HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")

# App constants
APP_TITLE = "PATOKA Chatbot"
APP_ICON = "🏥"
SIDEBAR_TITLE = "PATOKA Chatbot"
SIDEBAR_SUBTITLE = "Patient Touchpoint Knowledge Agent"

# Health check interval in seconds
HEALTH_CHECK_INTERVAL = 5


# API Configuration (if you have any)
# Add your API configurations here

# File upload settings
MAX_FILE_SIZE_MB = 10
ALLOWED_FILE_TYPES = ["pdf", "docx", "txt", "csv", "xlsx"]

# Chat settings
MAX_MESSAGES_PER_CONVERSATION = 100
STREAM_DELAY = 0.05  # Delay between words when streaming responses