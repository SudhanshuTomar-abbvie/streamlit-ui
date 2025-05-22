import json
import os
import streamlit as st
from utils.constants import HISTORY_FILE

def load_chat_history():
    """
    Load chat history from file
    
    Returns:
        dict: Conversations data
    """
    if os.path.exists(HISTORY_FILE):
        try:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading chat history: {e}")
            return {}
    return {}

def save_chat_history(conversations):
    """
    Save chat history to file
    
    Args:
        conversations (dict): Conversations data to save
    """
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(conversations, f)