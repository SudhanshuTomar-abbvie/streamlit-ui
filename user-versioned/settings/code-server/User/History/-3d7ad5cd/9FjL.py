import streamlit as st
import base64
import io
from PyPDF2 import PdfReader
from docx import Document
import requests
from datetime import datetime

# Constants
MAX_FILE_COUNT = 5
MAX_FILE_SIZE_MB = 2
ALLOWED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.doc']

# Helper Functions
def get_file_extension(filename):
    return filename.lower().split('.')[-1]

def extract_text_from_file(file):
    file_extension = get_file_extension(file.name)

    if file_extension == 'txt':
        return file.read().decode('utf-8')

    elif file_extension == 'pdf':
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    elif file_extension in ['docx', 'doc']:
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
        if text is None:
            continue
        encoded_content = encode_to_base64(text)
        file_list.append({
            "filename": file.name,
            "content": encoded_content
        })
    return {"files": file_list}

def render_ukb_page():
    # --- Streamlit App ---
    st.set_page_config(page_title="Document Processor", layout="wide")

    # --- Custom CSS for better style ---
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
        </style>
    """, unsafe'_allow_html=True)

    st.title("📄 Multi-document Uploader & Processor")

    # --- Document Upload Section ---
    with st.container():
        st.markdown("### 📁 Upload Your Documents")
        st.markdown('<div class="upload-container">', unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Upload up to 5 files (TXT, PDF, DOCX, DOC)",
            type=['txt', 'pdf', 'docx', 'doc'],
            accept_multiple_files=True,
            key="uploader"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # --- File Validation and Processing ---
    if uploaded_files:
        if len(uploaded_files) > MAX_FILE_COUNT:
            st.error(f"🚫 You can upload a maximum of {MAX_FILE_COUNT} files.")
        else:
            oversized_files = [f.name for f in uploaded_files if f.size > MAX_FILE_SIZE_MB * 1024 * 1024]
            if oversized_files:
                st.error(f"🚫 These files exceed the {MAX_FILE_SIZE_MB}MB limit: {', '.join(oversized_files)}")
            else:
                if st.button("🚀 Process Files"):
                    with st.spinner("⏳ Sending files to backend..."):
                        try:
                            payload = prepare_payload(uploaded_files)

                            # --- Replace with your actual backend endpoint ---
                            api_url = "http://k8s-default-dkumadse-f38d97347b-066209af6eb01332.elb.us-east-1.amazonaws.com:80/public/api/v1/chat/read_multiple_files/run"
                            
                            response = requests.post(api_url, json=payload)
                            result = response.json()

                            # --- MOCK: Simulated fallback ---
                            if not result or "combined_text" not in result:
                                result = {
                                    "combined_text": "\n".join([
                                        base64.b64decode(f['content']).decode('utf-8') for f in payload['files']
                                    ]),
                                    "file_count": len(payload['files']),
                                    "result": "Simulated backend response"
                                }

                            # Optionally store in session state for querying
                            st.session_state.extracted_doc_text = result["combined_text"]
                            st.session_state.active_doc_name = ", ".join([f.name for f in uploaded_files])
                            st.session_state.doc_query_mode = True

                            st.success("✅ Files processed successfully!")
                            st.subheader("📝 Combined Extracted Text")
                            st.text_area("Extracted Text", result.get("combined_text", ""), height=300)

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")