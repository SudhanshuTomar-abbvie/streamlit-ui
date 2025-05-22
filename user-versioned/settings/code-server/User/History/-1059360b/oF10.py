import streamlit as st
import os

def local_css(file_name: str):
    """
    Load custom CSS for styling
    """
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_message(message, img_content):
    """
    Render a single chat message with appropriate styling based on the role
    """
    if message["role"] == "user":
        st.markdown(
            f'''
            <div class="message user-message">
                <div class="message-content">{message["content"]}</div>
                <div class="avatar user-avatar">JD</div>
            </div>
            ''',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'''
            <div class="message bot-message">
                <div class="avatar bot-avatar">{img_content}</div>
                <div class="message-content">{message["content"]}</div>
            </div>
            ''',
            unsafe_allow_html=True
        )

def display_info_message(message):
    """
    Display an informational message with special styling
    """
    st.markdown(
        f'<div class="info-message">{message}</div>',
        unsafe_allow_html=True
    )

def display_success_message(message):
    """
    Display a success message with special styling
    """
    st.markdown(
        f'<div class="success-message">{message}</div>',
        unsafe_allow_html=True
    )

def display_error_message(message):
    """
    Display an error message with special styling
    """
    st.markdown(
        f'<div class="error-message">{message}</div>',
        unsafe_allow_html=True
    )