
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_info_page():
    """
    Render the information page with details about the chatbot
    """
    st.header("Information")
    
    st.subheader("About PATOKA Chatbot")
    st.write("PATOKA Chatbot (Patient Touchpoint Knowledge Agent) is a specialized AI assistant designed to help healthcare professionals understand and improve patient experiences.")
    
    st.subheader("Features")
    features = st.container()
    with features:
        st.write("• Answer questions about patient touchpoints and experiences")
        st.write("• Analyze patient feedback and sentiment")
        st.write("• Provide insights on improving patient satisfaction")
        st.write("• Suggest evidence-based approaches to common healthcare challenges")
    
    st.subheader("Data Sources")
    st.write("PATOKA Chatbot has been trained on:")
    sources = st.container()
    with sources:
        st.write("• Academic research on healthcare experiences")
        st.write("• Best practices in patient-centered care")
        st.write("• Anonymized patient feedback and surveys")
        st.write("• Healthcare quality improvement literature")
    
    st.subheader("Privacy & Security")
    st.write("All conversations with PATOKA Chatbot are confidential and secured. Patient identifying information should never be shared in conversations.")
    
    st.subheader("API Integration")
    st.write("PATOKA Chatbot is integrated with specialized healthcare ML models that provide:")
    api_features = st.container()
    with api_features:
        st.write("• Patient sentiment analysis")
        st.write("• Healthcare touchpoint classification")
        st.write("• Evidence-based response generation")
        st.write("• Document analysis and summarization")
    
    # Link to get help
    st.subheader("Need Help?")
    st.write("If you need assistance using PATOKA Chatbot or have any questions, please contact the support team.")