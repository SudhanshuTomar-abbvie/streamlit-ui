import streamlit as st
st.set_page_config(page_title="Upload Knowledge Docs", layout="wide")

import base64
import requests
from datetime import datetime
from utils.constants import DOCUMENT_QUERY_API_ENDPOINT, API_ENDPOINT
# Optional: Uncomment if using PDF or DOCX parsing
# from PyPDF2 import PdfReader
# from docx import Document

# Constants
MAX_FILE_COUNT = 5
MAX_FILE_SIZE_MB = 2

# --- Helper Functions ---
def get_file_extension(filename):
    return filename.lower().split('.')[-1]

def extract_text_from_file(file):
    ext = get_file_extension(file.name)

    if ext == 'txt':
        return file.read().decode('utf-8')
    elif ext == 'pdf':
        from PyPDF2 import PdfReader
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif ext in ['docx', 'doc']:
        from docx import Document
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return None

def encode_to_base64(text):
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def prepare_payload(files):
    file_list = []
    for file in files:
        text = extract_text_from_file(file)
        if text:
            encoded = encode_to_base64(text)
            file_list.append({
                "filename": file.name,
                "content": encoded
            })
    return {"files": file_list}

# --- Main Page Function ---
def render_ukb_page():
    if st.session_state.get("current_page") != "ukb":
        return

    st.markdown("""
        <style>
        .upload-container {
            border: 1px dashed #ccc;
            padding: 20px;
            border-radius: 5px;
            background-color: #f9f9f9;
            margin-bottom: 20px;
        }
        .stButton > button {
            width: 100%;
        }
        .centered-container {
            display: flex;
            justify-content: center;
            margin-bottom: 1em;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Input field for prompt ---
    def handle_enter():
        user_input_val = st.session_state.get("update_knowledge_bank", "")
        if user_input_val:
            st.session_state.pending_user_input = user_input_val
            st.session_state.current_page = "ukb"

    st.title("📄 Upload Knowledge Documents")

    st.markdown('<div class="upload-container">', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload up to 5 files (TXT, PDF, DOCX, DOC)",
        type=['txt', 'pdf', 'docx', 'doc'],
        accept_multiple_files=True,
        key="ukb_uploader"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("#### 👉 Ask a question related to uploaded documents")

    user_input = st.text_input(
        label="update_knowledge_bank",
        placeholder="Ask a question or provide context...",
        on_change=handle_enter,
        key="update_knowledge_bank",
        label_visibility="collapsed"
    )

    if st.button("🚀 Upload & Go to Chat"):
        if not uploaded_files:
            st.warning("Please upload at least one document.")
            return

        if len(uploaded_files) > MAX_FILE_COUNT:
            st.error(f"🚫 Max {MAX_FILE_COUNT} files allowed.")
            return

        oversized = [f.name for f in uploaded_files if f.size > MAX_FILE_SIZE_MB * 1024 * 1024]
        if oversized:
            st.error(f"🚫 These files exceed {MAX_FILE_SIZE_MB} MB: {', '.join(oversized)}")
            return

        with st.spinner("📡 Uploading and processing..."):
            try:
                payload = prepare_payload(uploaded_files)

                # --- Replace with your actual backend endpoint ---
                api_url = "http://k8s-default-dkumadse-f38d97347b-066209af6eb01332.elb.us-east-1.amazonaws.com:80/public/api/v1/chat/read_multiple_files/run"
                response = requests.post(api_url, json=payload)
                result = response.json()

                # Fallback mock
                if not result or "combined_text" not in result:
                    result = {
                        "combined_text": "\n".join([
                            base64.b64decode(f["content"]).decode("utf-8") for f in payload["files"]
                        ]),
                        "file_count": len(payload["files"]),
                        "result": "Simulated backend response"
                    }

                # Store in session for use in chat
                st.session_state.extracted_doc_text = result["combined_text"]
                st.session_state.active_doc_name = ", ".join([f.name for f in uploaded_files])
                st.session_state.doc_query_mode = True

                # Store prompt
                st.session_state.pending_user_input = user_input or "Document uploaded. Let's chat!"
                st.session_state.current_page = "chat"
                st.rerun()

            except Exception as e:
                st.error(f"❌ Failed to process files: {str(e)}")