import streamlit as st
from utils.leetcode import validate_leetcode_url
from utils.stream_handler import stream_response
from utils.llm_handler import get_gemini_response_stream
from utils.leetcode_api import fetch_leetcode_question

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


def initialize_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "proficiency_level" not in st.session_state:
        st.session_state.proficiency_level = None
    if "current_problem" not in st.session_state:
        st.session_state.current_problem = None
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "problem_details" not in st.session_state:
        st.session_state.problem_details = None

def display_problem_details():
    """Display problem details if available"""
    if st.session_state.problem_details:
        with st.sidebar:
            with st.expander("Problem Details", expanded=False):
                st.markdown(st.session_state.problem_details)

def display_full_problem_description(expanded=False):
    """Display full problem description with images"""
    if st.session_state.current_question:
        with st.expander("Full Problem Description", expanded=expanded):
            # Display formatted description with images
            st.markdown(st.session_state.current_question.get_formatted_description())
            

def main():
    st.set_page_config(
        page_title="DSA Teaching Assistant",
        page_icon="🎓",
        layout="wide"
    )
    
    # Initialize session state first
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
        
        # Validate and fetch problem details
        if leetcode_url:
            if validate_leetcode_url(leetcode_url):
                if leetcode_url != st.session_state.current_problem:
                    question = fetch_leetcode_question(leetcode_url)
                    if question:
                        st.session_state.current_problem = leetcode_url
                        st.session_state.current_question = question
                        
                        # Store problem details in session state
                        st.session_state.problem_details = f"""
                        **Problem**: {question.title} (LC{question.question_id})\n
                        **Difficulty**: {question.difficulty}\n
                        **Topics**: {', '.join(question.topic_tags)}\n
                        
                        **Similar Problems**:
                        {question._format_similar_questions()}
                        """
                        
                        # Clear messages when problem changes
                        st.session_state.messages = []
                        # Add system prompt as first message
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"👋 Hi! I'm your DSA Teaching Assistant. I'll help you with the problem: {question.title}"
                        })
                    else:
                        st.error("Failed to fetch problem details. Please try again.")
            else:
                st.error("Please enter a valid LeetCode URL")
        
        # Display problem details (in sidebar)
        display_full_problem_description(expanded=True)
        display_problem_details()

    
    display_full_problem_description()

    # Display current problem if exists
    if st.session_state.current_problem:
        st.success(f"Currently discussing: {st.session_state.current_problem}")
    
    # Display proficiency level if set
    if st.session_state.proficiency_level:
        st.info(f"Providing help suitable for {st.session_state.proficiency_level.split('(')[0].strip()} level")
    
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input handling
    if prompt := st.chat_input("Ask your doubt here..."):
        # Ensure there's a problem URL
        if not st.session_state.current_problem:
            st.warning("Please enter a LeetCode problem URL first!")
            return
        
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            response_stream = get_gemini_response_stream(
                prompt, 
                st.session_state.current_problem,
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