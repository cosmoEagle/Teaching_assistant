import streamlit as st
from components.leetcode import validate_leetcode_url
from components.stream_handler import stream_response
from components.llm_handler import get_gemini_response_stream
from components.leetcode_api import fetch_leetcode_question
from components.db_handler import DatabaseHandler
from components.history_sidebar import render_chat_history_sidebar
from utils.session_utils import initialize_session_state, clear_chat_history, save_current_chat
from ui.components.ui_utils import apply_custom_css, display_problem_details, display_full_problem_description

def process_leetcode_url(leetcode_url):
    """Process LeetCode URL input"""
    if validate_leetcode_url(leetcode_url):
        if leetcode_url != st.session_state.current_problem:
            question = fetch_leetcode_question(leetcode_url)
            if question:
                st.session_state.current_problem = leetcode_url
                st.session_state.current_question = question
                st.session_state.messages = []
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"👋 Hi! I'm your DSA Teaching Assistant. I'll help you with: {question.title}"
                })
                st.rerun()
            else:
                st.error("Failed to fetch problem details. Please try again.")
    else:
        st.error("Please enter a valid LeetCode URL")

def main():
    st.set_page_config(
        page_title="DSA Teaching Assistant",
        page_icon="🎓",
        layout="wide"
    )
    
    initialize_session_state()
    apply_custom_css()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration ⚙️")
        
        if st.button("New Discussion 🆕"):
            clear_chat_history()
        
        with st.expander("🎯 Proficiency Level", expanded=True):
            proficiency_level = st.radio(
                "Select your DSA proficiency level:",
                options=[
                    "Beginner (New to DSA)",
                    "Intermediate (Familiar with basic concepts)",
                    "Advanced (Comfortable with most DSA topics)"
                ],
                help="This helps me adjust my explanations to your level"
            )
            st.session_state.proficiency_level = proficiency_level
        
        with st.expander("🔗 Problem URL", expanded=True):
            default_url = st.session_state.get('leetcode_url_input', '')
            leetcode_url = st.text_input(
                "Enter LeetCode Problem URL:",
                value=default_url,
                key="leetcode_url_field",
                help="Paste the URL of the problem you need help with"
            )
            
            if leetcode_url:
                process_leetcode_url(leetcode_url)
        
        render_chat_history_sidebar(st.session_state.db_handler)
        
        display_full_problem_description(expanded=True)
        display_problem_details()
    
    display_full_problem_description()

    if st.session_state.current_problem:
        st.success(f"Currently discussing: {st.session_state.current_question.title}")
    
    if st.session_state.messages and st.session_state.current_problem:
        save_current_chat()

    if st.session_state.proficiency_level:
        st.info(f"Providing help suitable for {st.session_state.proficiency_level.split('(')[0].strip()} level")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask your doubt here..."):
        if not st.session_state.current_problem:
            st.warning("Please enter a LeetCode problem URL first!")
            return
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
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
                save_current_chat()

if __name__ == "__main__":
    main()