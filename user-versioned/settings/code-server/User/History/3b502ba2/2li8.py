import streamlit as st
import os
import sys
from pathlib import Path

# Add the project directory to the Python path to allow imports
PROJECT_PATH = Path(__file__).parent
sys.path.append(str(PROJECT_PATH))

# Import utilities
from utils.constants import APP_TITLE, APP_ICON
from utils.session_state import init_session_state
from utils.rendering import local_css

# Import services
from services.health_service import start_health_check_thread, stop_health_check_thread
from services.history_service import ensure_history_file_exists

# Import components
from components.sidebar import render_sidebar

# Import pages
from ui.home_page import render_home_page
from ui.chat_page import render_chat_page
from ui.history_page import render_history_page
from ui.info_page import render_info_page
from ui.settings_page import render_settings_page
from ui.update_knowledge_bank import render_ukb_page

def main():
    """
    Main function to run the Streamlit app
    """
    # Set page configuration
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state variables
    init_session_state()

    # Ensure the history file exists
    ensure_history_file_exists()

    # Load custom CSS
    local_css("style.css")

    # Start the health check background thread
    start_health_check_thread()

    try:
        # Render the sidebar
        render_sidebar()

        # === Only render the current page ===
        current_page = st.session_state.get("current_page", "home")

        if current_page == "home":
            render_home_page()
        elif current_page == "chat":
            render_chat_page()
        elif current_page=="ukb":
            render_ukb_page()
        elif current_page == "conversation_history":
            render_history_page()
        elif current_page == "information":
            render_info_page()
        else:
            # If unknown page, default to home
            st.session_state.current_page = "home"
            st.rerun()

        # Footer for all pages
        st.markdown(
            '<div class="footer">BTS Patient Services | Powered by MLOPS </div>',
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        import traceback
        st.exception(e)


if __name__ == "__main__":
    main()
