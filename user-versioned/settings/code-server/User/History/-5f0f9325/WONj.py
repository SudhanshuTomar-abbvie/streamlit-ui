
import streamlit as st
import requests
import tempfile
import os
import tiktoken
from unstructured.partition.auto import partition
from utils.constants import DOCUMENT_QUERY_API_ENDPOINT


def extract_text_from_file(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        elements = partition(tmp_file_path)
        text = "\n\n".join([str(e) for e in elements])
    finally:
        os.unlink(tmp_file_path)

    return text

def truncate_text_to_token_limit(text, max_tokens=5000, encoding_name="cl100k_base"):
    tokenizer = tiktoken.get_encoding(encoding_name)
    tokens = tokenizer.encode(text)

    if len(tokens) <= max_tokens:
        return text

    truncated = tokenizer.decode(tokens[:max_tokens])
    return truncated

def process_document(file):
    full_text = extract_text_from_file(file)
    truncated_text = truncate_text_to_token_limit(full_text)

    tokenizer = tiktoken.get_encoding("cl100k_base")
    return {
        "filename": file.name,
        "original_token_count": len(tokenizer.encode(full_text)),
        "truncated_token_count": len(tokenizer.encode(truncated_text)),
        "text": truncated_text
    }

def query_document(query, document_text):
    try:
        payload = {
            "query": query,
            "extracted_text": document_text,
            "token_threshold": 5000
        }

        # Debug information
        st.session_state.debug_info = {
            "endpoint": DOCUMENT_QUERY_API_ENDPOINT,
            "payload_size": len(str(payload))
        }

        response = requests.post(
            DOCUMENT_QUERY_API_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        st.session_state.debug_info["status_code"] = response.status_code
        st.session_state.debug_info["response_size"] = len(response.text)
        st.session_state.debug_info["raw_response"] = response.text[:1000]

        if response.status_code != 200:
            raise Exception(f"API returned {response.status_code}: {response.text}")

        try:
            result = response.json()
            if isinstance(result, str):
                return {"answer": result}
            elif isinstance(result, dict):
                if "answer" not in result:
                    for key in ["response", "result", "text", "content", "message"]:
                        if key in result:
                            result["answer"] = result[key]
                            break
                    else:
                        result["answer"] = str(result)
                return result
            return {"answer": str(result)}
        except ValueError:
            return {"answer": response.text}
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")