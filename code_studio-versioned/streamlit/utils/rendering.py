import streamlit as st
import os

def local_css(file_name: str):
    """
    Load custom CSS for styling
    """
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_svg(svg_file_path):
    """
    Renders the given svg string from file.
    """
    try:
        with open(svg_file_path, "r") as f:
            svg_content = f.read()
        return svg_content
    except FileNotFoundError:
        # If SVG file not found, return a placeholder SVG
        return create_placeholder_svg()

def create_placeholder_svg():
    """
    Creates a placeholder SVG with 'ML' text in it
    """
    return '''
    <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="45" fill="#2e3191" />
        <text x="50" y="60" font-family="Arial" font-size="30" fill="white" text-anchor="middle">ML</text>
    </svg>
    '''

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