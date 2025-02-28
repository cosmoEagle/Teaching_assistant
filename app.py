import streamlit as st
from utils.leetcode import validate_leetcode_url
from utils.stream_handler import stream_response
from utils.llm_handler import get_gemini_response_stream

def initialize_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "proficiency_level" not in st.session_state:
        st.session_state.proficiency_level = None


def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
    .chat-container {
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    .user-message {
        background-color: #e6f3ff;
        text-align: right;
    }
    .assistant-message {
        background-color: #f0f0f0;
    }
    .sidebar .stRadio > div {
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="DSA Teaching Assistant",
        page_icon="🎓",
        layout="wide"
    )
    
    initialize_session_state()
    apply_custom_css()
    
    st.title("DSA Teaching Assistant 🎓")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # DSA Proficiency Selector
        proficiency_level = st.radio(
            "What's your DSA proficiency level?",
            options=[
                "Beginner (New to DSA)",
                "Intermediate (Familiar with basic concepts)",
                "Advanced (Comfortable with most DSA topics)"
            ],
            help="This helps me adjust my explanations to your level"
        )
        st.session_state.proficiency_level = proficiency_level
        
        st.divider()
        
        # LeetCode URL input
        leetcode_url = st.text_input(
            "Enter LeetCode Problem URL:",
            help="Paste the URL of the problem you need help with"
        )
        if leetcode_url and not validate_leetcode_url(leetcode_url):
            st.error("Please enter a valid LeetCode URL")
    
    # Display proficiency level indicator
    if st.session_state.proficiency_level:
        st.info(f"Providing help suitable for {st.session_state.proficiency_level.split('(')[0].strip()} level")
    
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input handling
    if prompt := st.chat_input("Ask your doubt here..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            response_stream = get_gemini_response_stream(
                prompt, 
                leetcode_url, 
                st.session_state.messages,
                st.session_state.proficiency_level
            )
            
            full_response = stream_response(response_stream)
            
            if not isinstance(full_response, str) or not full_response.startswith("An error occurred"):
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

if __name__ == "__main__":
    main()