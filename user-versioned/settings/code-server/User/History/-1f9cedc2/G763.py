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
        "original_token_count": original_token_count,
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
        # Match the backend endpoint's expected parameter names
        payload = {
            "query": query,
            "extracted_text": document_text,
            "token_threshold": 5000
        }
        
        # Enable debugging
        st.session_state.debug_info = {
            "endpoint": DOCUMENT_QUERY_API_ENDPOINT,
            "payload_size": len(str(payload))
        }
        
        # Make the API call
        response = requests.post(
            DOCUMENT_QUERY_API_ENDPOINT, 
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Print response details for debugging
        st.session_state.debug_info["status_code"] = response.status_code
        st.session_state.debug_info["response_size"] = len(response.text)
        
        # Store raw response for debugging
        st.session_state.debug_info["raw_response"] = response.text[:1000]  # First 1000 chars
        
        # Check if response was successful
        if response.status_code != 200:
            raise Exception(f"API returned status code {response.status_code}: {response.text}")
        
        # Try to parse JSON response
        try:
            result = response.json()
            # For simple string responses, create a proper structure
            if isinstance(result, str):
                return {"answer": result}
            # For dict responses, ensure we have an answer field
            elif isinstance(result, dict):
                if "answer" not in result:
                    # Look for other possible keys that might contain the answer
                    for key in ["response", "result", "text", "content", "message"]:
                        if key in result:
                            result["answer"] = result[key]
                            break
                    else:
                        # If no known keys found, just use the whole response
                        result["answer"] = str(result)
                return result
            else:
                # For other types, convert to string and wrap in dict
                return {"answer": str(result)}
        except ValueError:
            # If response is not valid JSON, return as plain text
            return {"answer": response.text}
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")

def document_chat_app():
    st.title("Document Chat")
    
    # Initialize session state for conversation history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'document_text' not in st.session_state:
        st.session_state.document_text = None
        
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None
    
    # Sidebar for document upload
    with st.sidebar:
        st.header("Upload Document")
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt", "csv", "xlsx", "pptx", "html", "md"])
        
        if uploaded_file is not None and (st.session_state.current_document != uploaded_file.name):
            with st.spinner("Processing document..."):
                try:
                    # Process document
                    result = process_document(uploaded_file)
                    
                    # Store document text in session state
                    st.session_state.document_text = result['text']
                    st.session_state.current_document = uploaded_file.name
                    
                    # Clear previous conversation when new document is uploaded
                    st.session_state.messages = []
                    
                    # Add system message about the new document
                    st.session_state.messages.append({
                        "role": "system",
                        "content": f"Document '{uploaded_file.name}' loaded ({result['truncated_token_count']}/5000 tokens)"
                    })
                    
                    st.success(f"Document processed: {uploaded_file.name}")
                    
                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
        
        # Document info
        if st.session_state.current_document:
            st.info(f"Current document: {st.session_state.current_document}")
            if st.button("Clear document"):
                st.session_state.document_text = None
                st.session_state.current_document = None
                st.session_state.messages = []
                if 'debug_info' in st.session_state:
                    st.session_state.pop('debug_info')
                st.rerun()
                
        # Optionally add test connection button
        if st.button("Test API Connection"):
            try:
                # Simple test call to API using the correct parameter names
                test_payload = {
                    "query": "test", 
                    "extracted_text": "This is a test document content.",
                    "token_threshold": 5000
                }
                response = requests.post(
                    DOCUMENT_QUERY_API_ENDPOINT,
                    json=test_payload,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    st.success(f"API connection successful! Status code: {response.status_code}")
                    try:
                        st.json(response.json())
                    except:
                        st.text(f"Response: {response.text[:100]}...")
                else:
                    st.error(f"API returned status code {response.status_code}")
                    st.text(f"Response: {response.text[:100]}...")
            except Exception as e:
                st.error(f"Connection test failed: {str(e)}")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(message["content"])
        elif message["role"] == "system":
            with st.chat_message("system"):
                st.info(message["content"])
    
    # Chat input
    if query := st.chat_input("Ask a question about your document..."):
        # Only allow queries if a document is loaded
        if st.session_state.document_text is None:
            with st.chat_message("system"):
                st.warning("Please upload a document first.")
        else:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Display user message
            with st.chat_message("user"):
                st.write(query)
            
            # Get response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Get answer from API
                        response = query_document(query, st.session_state.document_text)
                        answer = response.get("answer", "I couldn't find an answer to that question in the document.")
                        
                        # Display answer
                        st.write(answer)
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        # Show debug info if available (can be removed in production)
                        if 'debug_info' in st.session_state and st.session_state.debug_info:
                            with st.expander("Debug Information"):
                                st.json(st.session_state.debug_info)
                                if "raw_response" in st.session_state.debug_info:
                                    st.text(st.session_state.debug_info["raw_response"][:500] + "...")
                        
                    except Exception as e:
                        error_msg = f"Error getting answer: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "system", "content": error_msg})
                        
                        # Add troubleshooting options
                        st.info("Troubleshooting:")
                        if st.button("Show API Request Details"):
                            st.json({
                                "endpoint": DOCUMENT_QUERY_API_ENDPOINT,
                                "payload_structure": {
                                    "query": "Your question (length: " + str(len(query)) + ")",
                                    "context": "Document text (length: " + str(len(st.session_state.document_text)) + ")"
                                }
                            })

if __name__ == "__main__":
    document_chat_app()