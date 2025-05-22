import streamlit as st
import base64
import io
from PyPDF2 import PdfReader
from docx import Document
import requests

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

# Streamlit App
st.title("Multi-file Uploader and Processor")

uploaded_files = st.file_uploader(
    "Upload up to 5 files (txt, pdf, docx)",
    type=['txt', 'pdf', 'docx', 'doc'],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > MAX_FILE_COUNT:
        st.error(f"You can upload a maximum of {MAX_FILE_COUNT} files.")
    else:
        oversized_files = [f.name for f in uploaded_files if f.size > MAX_FILE_SIZE_MB * 1024 * 1024]
        if oversized_files:
            st.error(f"These files exceed the {MAX_FILE_SIZE_MB}MB limit: {', '.join(oversized_files)}")
        else:
            if st.button("Process Files"):
                with st.spinner("Processing..."):
                    try:
                        payload = prepare_payload(uploaded_files)

                        
                        response = requests.post("http://k8s-default-dkumadse-f38d97347b-066209af6eb01332.elb.us-east-1.amazonaws.com:80/public/api/v1/chat/read_multiple_files/run", json=payload)
                        result = response.json()

                        ### MOCK: Simulate the backend call
                        result = {
                            "combined_text": "\n".join([base64.b64decode(f['content']).decode('utf-8') for f in payload['files']]),
                            "file_count": len(payload['files']),
                            "result": "Backend processing simulated successfully"
                        }

                        st.success("Files processed successfully!")
                        st.subheader("Combined Text")
                        st.text_area("Extracted Text", result.get("combined_text", ""), height=300)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")