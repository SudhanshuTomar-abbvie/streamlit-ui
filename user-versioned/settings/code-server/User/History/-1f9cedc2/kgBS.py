import streamlit as st
import requests
from config.settings import API_ENDPOINT

def realtime_qna():
    st.title("Document Upload and Extraction")

    # File uploader
    uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "txt"])
    # Constants
    BACKEND_API_BASE_URL = "http://dku-mad-service-mlopschatbot-on-mlops-poc:12000/public/api/v1"
    API_ENDPOINT = f"{BACKEND_API_BASE_URL}/mlopsChatbot/ChatOnDocument/run"

    if uploaded_file is not None:
        st.success("File uploaded successfully!")

        # Button to trigger API call
        if st.button("Extract Data"):
            # Send file to backend API endpoint
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post(API_ENDPOINT, files=files)

            if response.status_code == 200:
                st.write("Data extracted:")
                st.json(response.json())
            else:
                st.error("Failed to extract data.")