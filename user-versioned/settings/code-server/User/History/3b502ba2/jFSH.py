import streamlit as st
import datetime
import time
import random

# Set page configuration
st.set_page_config(
    page_title="MLOPS Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
def local_css(file_name: str):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# load your external stylesheet
local_css("style.css")



# Function to render SVG content
def render_svg(svg_file_path):
    """Renders the given svg string."""
    try:
        with open(svg_file_path, "r") as f:
            svg_content = f.read()
        return svg_content
    except FileNotFoundError:
        # If SVG file not found, return a placeholder SVG
        return create_placeholder_svg()

def create_placeholder_svg():
    """Creates a placeholder SVG with 'ML' text in it"""
    return '''
    <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="45" fill="#2e3191" />
        <text x="50" y="60" font-family="Arial" font-size="30" fill="white" text-anchor="middle">ML</text>
    </svg>
    '''

# Set your logo path - change this to your actual SVG file path
LOGO_PATH = "avalogo.svg"
# Get SVG content just once to reuse
img_content = render_svg(LOGO_PATH)
# st.image("download.png", width = 120)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = [
        {
            "title": "Patient discharge process inquiry",
            "last_message": "Yesterday at 2:15 PM",
            "message_count": 8
        },
        {
            "title": "Emergency room wait times",
            "last_message": "April 20, 2025",
            "message_count": 12
        },
        {
            "title": "Patient feedback analysis",
            "last_message": "April 18, 2025",
            "message_count": 5
        }
    ]
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'health_status' not in st.session_state:
    st.session_state.health_status = True

# Function to simulate API responses
def simulate_api_response(message):
    responses = [
        "Based on our patient satisfaction data, discharge instructions are often cited as an area for improvement. Patients report wanting clearer follow-up care guidelines.",
        "Our analysis shows that ER wait times are most affected by triage efficiency and staffing patterns. The average wait time has decreased by 12% since implementing the new triage protocol.",
        "Patient feedback indicates that communication from healthcare providers is the single most important factor in overall satisfaction scores.",
        "According to recent surveys, 68% of patients prefer to receive follow-up information via secure patient portal, while 22% prefer phone calls.",
        "Looking at the data from last quarter, medication reconciliation errors decreased by 23% after implementing the new double-check protocol.",
        "Our touchpoint analysis reveals that the admission process is rated lower in satisfaction compared to other healthcare touchpoints.",
    ]
    time.sleep(1)  # Simulate API delay
    return random.choice(responses)

# Function to handle new messages
def handle_message(message):
    if message.strip():  # Only process non-empty messages
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": message})
        
        # Get bot response (simulated)
        bot_response = simulate_api_response(message)
        
        # Add bot response to chat
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    
# Sidebar
with st.sidebar:
    st.sidebar.image("abbvielogo.png")
    st.markdown('<div class="sidebar-title">MLOPS Chatbot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Patient Touchpoint Knowledge Agent</div>', unsafe_allow_html=True)
    
    # Create buttons for navigation
    if st.button("🏠 Home", key="nav_home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    if st.button("💬 Chat", key="nav_chat"):
        st.session_state.current_page = "chat"
        st.rerun()
    
    if st.button("📊 Conversation History", key="nav_history"):
        st.session_state.current_page = "conversation_history"
        st.rerun()
    
    if st.button("ℹ️ Information", key="nav_info"):
        st.session_state.current_page = "information"
        st.rerun()
    
    if st.button("⚙️ Settings", key="nav_settings"):
        st.session_state.current_page = "settings"
        st.rerun()
    
    # Health status indicator
    status_class = "healthy" if st.session_state.health_status else "unhealthy"
    status_text = "System Online" if st.session_state.health_status else "System Offline"
    
    st.markdown(
        f'<div class="health-indicator"><div class="health-status {status_class}"></div>{status_text}</div>',
        unsafe_allow_html=True
    )
    
    # User info at bottom
    st.markdown(
        '<div class="user-info">John Doe<br><a href="#" style="color: white; text-decoration: none;">Logout</a></div>',
        unsafe_allow_html=True
    )

# Home page
if st.session_state.current_page == "home":
    
    st.markdown('<div class="welcome-container">', unsafe_allow_html=True)
    # Replace PA with logo
    # st.image("download.png")
    # st.markdown(f'<div class="welcome-logo">{img_content}</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center !important;" class="welcome-title">Welcome to MLOPS Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center !important;" class="welcome-subtitle">Patient Touchpoint Knowledge Agent</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center !important;" >A generative AI chatbot designed to provide insights about patient touchpoints and healthcare experiences.</p>', unsafe_allow_html=True)
    
    # Search box with fixed alignment
    # st.markdown('<div class="input-group">', unsafe_allow_html=True)
    
    # col1, col2 = st.columns([3, 1])
    
    # with col1:
    #     st.markdown('<div class="input-field">', unsafe_allow_html=True)
    #     user_input = st.text_input("Ask any question...", key="home_input")
    #     st.markdown('</div>', unsafe_allow_html=True)
    
    # with col2:
    #     st.markdown('<div class="input-button">', unsafe_allow_html=True)
    #     if st.button("Ask and Go to Chat", key="home_ask_button"):
    #         if user_input:
    #             handle_message(user_input)
    #             st.session_state.current_page = "chat"
    #             st.rerun()
    #     st.markdown('</div>', unsafe_allow_html=True)

    # Container for both input and button
    st.markdown('<div class="centered-container">', unsafe_allow_html=True)

    # Text input with default value
    user_input = st.text_input(
        "Ask any question...",
        value="What factors most impact patient satisfaction?",
        key="home_input",
        label_visibility="collapsed"
    )

    # Button
    if st.button("Ask and Go to Chat", key="home_ask_button"):
        if user_input:
            handle_message(user_input)
            st.session_state.current_page = "chat"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Popular questions
    st.markdown('<h2 style="text-align:center; margin-top:40px;">Popular Questions</h2>', unsafe_allow_html=True)
    
    popular_questions = [
        "What are common patient complaints during discharge?",
        "How can we improve ER wait times?",
        "What factors most impact patient satisfaction?",
        "How do patients prefer to receive follow-up information?"
    ]
    
    # Arrange popular questions in 2 columns
    cols = st.columns(2)
    for i, question in enumerate(popular_questions):
        with cols[i % 2]:
            if st.button(question, key=f"popular_q_{i}"):
                handle_message(question)
                st.session_state.current_page = "chat"
                st.rerun()

# Chat page
elif st.session_state.current_page == "chat":
    st.header("Conversation with MLOPS Chatbot")
    st.markdown(f'<p class="last-updated">Last updated: {datetime.datetime.now().strftime("%H:%M:%S %p")}</p>', unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        if not st.session_state.messages:
            # Initial welcome message with logo
            st.markdown(
                f'''
                <div class="message bot-message">
                    <div class="avatar bot-avatar">{img_content}</div>
                    <div class="message-content">
                        MLOPS Chatbot is ready to assist you<br>
                        Ask a question about patient touchpoints or healthcare experiences
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
        else:
            # Display all messages
            for message in st.session_state.messages:
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
                            # <div class="avatar bot-avatar">{img_content}</div>
                            <div class="message-content">{message["content"]}</div>
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area with fixed alignment
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="input-group">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown('<div class="input-field">', unsafe_allow_html=True)
        user_input = st.text_input("Ask MLOPS Chatbot about patient touchpoints...", key="chat_input")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div style=" class="input-button">', unsafe_allow_html=True)
        if st.button("Send", key="send_button"):
            if user_input:
                handle_message(user_input)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Conversation History page
elif st.session_state.current_page == "conversation_history":
    st.header("Conversation History")
    
    st.markdown("<h3>Review your previous conversations with MLOPS Chatbot.</h3>", unsafe_allow_html=True)
    
    history_container = st.container()
    
    with history_container:
        for i, conversation in enumerate(st.session_state.conversation_history):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{conversation['title']}**")
                st.markdown(f"Last message: {conversation['last_message']}")
            with col2:
                st.markdown(f"{conversation['message_count']} messages")
                if st.button("View", key=f"view_conv_{i}"):
                    st.session_state.current_page = "chat"
                    st.rerun()
            st.markdown("---")

# Information page
elif st.session_state.current_page == "information":
    st.header("Information")
    
    st.subheader("About MLOPS Chatbot")
    st.write("MLOPS Chatbot (Patient Touchpoint Knowledge Agent) is a specialized AI assistant designed to help healthcare professionals understand and improve patient experiences.")
    
    st.subheader("Features")
    features = st.container()
    with features:
        st.write("• Answer questions about patient touchpoints and experiences")
        st.write("• Analyze patient feedback and sentiment")
        st.write("• Provide insights on improving patient satisfaction")
        st.write("• Suggest evidence-based approaches to common healthcare challenges")
    
    st.subheader("Data Sources")
    st.write("MLOPS CHatbot has been trained on:")
    sources = st.container()
    with sources:
        st.write("• Academic research on healthcare experiences")
        st.write("• Best practices in patient-centered care")
        st.write("• Anonymized patient feedback and surveys")
        st.write("• Healthcare quality improvement literature")
    
    st.subheader("Privacy & Security")
    st.write("All conversations with MLOPS Chatbot are confidential and secured. Patient identifying information should never be shared in conversations.")

# Settings page
elif st.session_state.current_page == "settings":
    st.header("Settings")
    
    st.subheader("Account Settings")
    st.text_input("Name", value="John Doe")
    st.text_input("Email", value="john.doe@example.com")
    
    st.subheader("Notification Preferences")
    st.checkbox("Email notifications for new insights", value=True)
    st.checkbox("Weekly summary reports", value=False)
    
    st.subheader("Interface Settings")
    st.select_slider("Chat message size", options=["Small", "Medium", "Large"], value="Medium")
    selected_color = st.color_picker("Theme color", "#2e3191")
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

# Footer on all pages
st.markdown('<div class="footer">BTS Patient Services | Powered by MLOPS </div>', unsafe_allow_html=True)