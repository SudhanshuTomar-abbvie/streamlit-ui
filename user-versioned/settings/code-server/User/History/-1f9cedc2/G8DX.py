import streamlit as st
import requests
import tempfile
import os
import tiktoken
from unstructured.partition.auto import partition
from config.settings import DOCUMENT_PROCESS_API_ENDPOINT

def extract_text_from_file(file):
    """
    Extract text from uploaded file using Unstructured library.
    
    Args:
        file: Streamlit uploaded file object
    
    Returns:
        str: Extracted text from the document
    """
    # Create a temporary file to save the uploaded content
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        # Use unstructured to extract text
        elements = partition(tmp_file_path)
        # Join all text elements
        text = "\n\n".join([str(element) for element in elements])
    finally:
        # Clean up the temporary file
        os.unlink(tmp_file_path)
    
    return text

def truncate_text_to_token_limit(text, max_tokens=5000, encoding_name="cl100k_base"):
    """
    Truncate text to stay within the specified token limit.
    
    Args:
        text (str): Input text to truncate
        max_tokens (int): Maximum number of tokens to keep
        encoding_name (str): Name of the tokenizer encoding to use
    
    Returns:
        str: Truncated text within token limit
    """
    # Initialize tokenizer
    tokenizer = tiktoken.get_encoding(encoding_name)
    
    # Encode text to tokens
    tokens = tokenizer.encode(text)
    
    # If text is already within limits, return it as is
    if len(tokens) <= max_tokens:
        return text
    
    # Otherwise, truncate tokens and decode back to text
    truncated_tokens = tokens[:max_tokens]
    truncated_text = tokenizer.decode(truncated_tokens)
    
    return truncated_text

def process_document(file):
    """
    Process an uploaded document: extract text and truncate to token limit.
    
    Args:
        file: Streamlit uploaded file object
    
    Returns:
        dict: Processed document information with extracted and truncated text
    """
    # Extract full text from file
    full_text = extract_text_from_file(file)
    
    # Truncate text to 5000 tokens
    truncated_text = truncate_text_to_token_limit(full_text, max_tokens=5000)
    
    # Count tokens in original and truncated text
    tokenizer = tiktoken.get_encoding("cl100k_base")
    original_token_count = len(tokenizer.encode(full_text))
    truncated_token_count = len(tokenizer.encode(truncated_text))
    
    return {
        "filename": file.name,
        "original_text_length": len(full_text),
        "original_token_count": original_token_count,
        "truncated_text_length": len(truncated_text),
        "truncated_token_count": truncated_token_count,
        "text": truncated_text
    }

def realtime_qna():
    st.title("Document Upload and Extraction")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "txt", "csv", "xlsx", "pptx", "html", "md"])
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        
        # Options for processing
        with st.expander("Processing Options"):
            token_limit = st.slider("Token Limit", min_value=100, max_value=10000, value=5000, step=100)
            process_locally = st.checkbox("Process document locally", value=True)
        
        # Button to process document
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                if process_locally:
                    # Process document locally using Unstructured
                    try:
                        result = process_document(uploaded_file)
                        
                        # Display processing results
                        st.subheader("Processing Results")
                        st.write(f"Original length: {result['original_text_length']} characters / {result['original_token_count']} tokens")
                        st.write(f"Truncated length: {result['truncated_text_length']} characters / {result['truncated_token_count']} tokens")
                        
                        # Preview of extracted text
                        with st.expander("View Extracted Text"):
                            st.text_area("Extracted content (truncated to token limit)", result['text'], height=300)
                        
                        # Save the processed text in session state for further use
                        st.session_state.processed_text = result['text']
                        st.session_state.processed_file_name = result['filename']
                        
                    except Exception as e:
                        st.error(f"Error processing document: {str(e)}")
                else:
                    # Send file to backend API endpoint
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        response = requests.post(DOCUMENT_PROCESS_API_ENDPOINT, files=files)
                        
                        if response.status_code == 200:
                            st.subheader("API Response")
                            st.json(response.json())
                        else:
                            st.error(f"Failed to extract data. Status code: {response.status_code}")
                    except Exception as e:
                        st.error(f"API connection error: {str(e)}")

if __name__ == "__main__":
    realtime_qna()