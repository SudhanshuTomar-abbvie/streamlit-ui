import streamlit as st
import requests
import tempfile
import os
import tiktoken
from unstructured.partition.auto import partition
from config.settings import DOCUMENT_QUERY_API_ENDPOINT

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

def query_document(query, document_text):
    """
    Send a query to the API endpoint along with the document text.
    
    Args:
        query (str): User's question about the document
        document_text (str): Extracted and truncated text from the document
    
    Returns:
        dict: Response from the API containing the answer
    """
    try:
        payload = {
            "query": query,
            "extracted_text": document_text
        }
        
        response = requests.post(DOCUMENT_QUERY_API_ENDPOINT, json=payload)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get response from query API: {str(e)}")

def realtime_qna():
    st.title("Document Q&A")
    
    # Initialize session state for storing document text
    if 'processed_text' not in st.session_state:
        st.session_state.processed_text = None
        
    if 'document_processed' not in st.session_state:
        st.session_state.document_processed = False
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "txt", "csv", "xlsx", "pptx", "html", "md"])
    
    # Process document when uploaded
    if uploaded_file is not None and not st.session_state.document_processed:
        with st.spinner("Processing document..."):
            try:
                # Process document locally using Unstructured
                result = process_document(uploaded_file)
                
                # Save the processed text in session state
                st.session_state.processed_text = result['text']
                st.session_state.document_processed = True
                
                # Show brief success message with document stats
                st.success(f"Document processed: {uploaded_file.name} ({result['truncated_token_count']}/5000 tokens)")
                
                # Option to view extracted text if needed
                with st.expander("View Extracted Text"):
                    st.text_area("Content", result['text'], height=200)
                    
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
    
    # Query interface - only show if document is processed
    if st.session_state.document_processed:
        st.subheader("Ask questions about your document")
        query = st.text_input("Your question:")
        
        if query:
            if st.button("Get Answer"):
                with st.spinner("Getting answer..."):
                    try:
                        # Get answer from API
                        response = query_document(query, st.session_state.processed_text)
                        
                        # Display the answer
                        st.subheader("Answer")
                        st.write(response.get("answer", "No answer available"))
                        
                        # Display sources or context if provided in the response
                        if "sources" in response:
                            with st.expander("Sources"):
                                st.write(response["sources"])
                                
                    except Exception as e:
                        st.error(f"Error getting answer: {str(e)}")
    
    # Button to reset and upload a new document
    if st.session_state.document_processed:
        if st.button("Process a new document"):
            st.session_state.document_processed = False
            st.session_state.processed_text = None
            st.experimental_rerun()

if __name__ == "__main__":
    realtime_qna()