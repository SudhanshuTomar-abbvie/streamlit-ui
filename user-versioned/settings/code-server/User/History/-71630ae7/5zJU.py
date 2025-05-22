import requests
import logging
import time
import json
import streamlit as st
from config.settings import API_ENDPOINT

def query_llm(prompt, chat_history=None, retries=3, delay=2):
    """
    Call the LLM API endpoint with retry mechanism
    
    Args:
        prompt (str): User prompt
        chat_history (list, optional): Previous messages
        retries (int): Number of retry attempts
        delay (int): Delay between retries in seconds
        
    Returns:
        dict: Response with text and context
    """
    for attempt in range(retries):
        try:
            # Prepare the payload
            payload = {"user_query": prompt}
            
            # Format chat history if needed
            if chat_history and len(chat_history) > 0:
                context_prompt = "Previous conversation:\n"
                for msg in chat_history:
                    if msg["role"] == "user":
                        context_prompt += f"User: {msg['content']}\n"
                    else:
                        context_prompt += f"Assistant: {msg['content']}\n"
                context_prompt += "\nCurrent query: "
                
                # Combine context with current prompt
                payload["user_query"] = context_prompt + prompt
            
            # Debug the payload
            st.session_state.last_payload = payload
            logging.debug(f"Payload being sent: {payload}")
            
            # Make API call
            response = requests.post(
                API_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            
            logging.debug(f"Raw API Response: {data}")
            print(data)
            # Extract data from response
            if isinstance(data, dict):
                response_text = data["response"][""]
                context = data["response"]
            else:
                response_text = data.get("response", "No response available")
                context = data.get("contexts", ["No context available"])
            
            return {
                "response": response_text,
                "context": context
            }
                
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                error_msg = f"Error communicating with LLM service: {str(e)}"
                logging.error(error_msg)
                return {
                    "response": f"Sorry, I encountered an error: {str(e)}",
                    "context": []
                }