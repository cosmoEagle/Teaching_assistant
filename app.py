import streamlit as st
from utils.leetcode import validate_leetcode_url
from utils.stream_handler import stream_response
from utils.llm_handler import get_gemini_response_stream
from utils.leetcode_api import fetch_leetcode_question
from utils.db_handler import DatabaseHandler
from components.history_sidebar import render_chat_history_sidebar
from datetime import datetime

def apply_custom_css():
    """Apply custom CSS with performance optimizations"""
    st.markdown("""
        <style>
        /* Optimize container rendering */
        .stApp {
            contain: content;
        }
        
        /* Reduce repaints */
        .sidebar .element-container {
            transform: translateZ(0);
        }
        
        /* Optimize markdown rendering */
        .markdown-text-container {
            contain: content;
        }
        </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state"""
    if "db_handler" not in st.session_state:
        st.session_state.db_handler = DatabaseHandler()
    
    # Initialize other states only if needed
    defaults = {
        "messages": [],
        "proficiency_level": "Intermediate (Familiar with basic concepts)",
        "current_problem": None,
        "current_question": None,
        "problem_details": None,
    }
    
    st.session_state.update({
        k: st.session_state.get(k, v)
        for k, v in defaults.items()
    })
    
def clear_chat_history():
    """Clear current chat history and selection"""
    # Clear all relevant session state variables
    st.session_state.messages = []
    st.session_state.current_problem = None
    st.session_state.current_question = None
    st.session_state.problem_details = None
    st.session_state.leetcode_url_input = ''  # Add this line to clear the URL input
    st.rerun()


def display_problem_details():
    """Display problem details if available"""
    if st.session_state.problem_details:
        with st.sidebar:
            with st.expander("📝 Problem Overview", expanded=False):
                # Get problem details
                details = st.session_state.problem_details
                
                # Display title and difficulty with emoji based on difficulty
                difficulty_emoji = {
                    'Easy': '🟢',
                    'Medium': '🟡',
                    'Hard': '🔴'
                }.get(details['difficulty'], '⚪')
                
                st.markdown(f"### {details['title']}")
                st.markdown(f"**Difficulty**: {difficulty_emoji} {details['difficulty']}")
                
                # Display topics
                if 'topics' in details:
                    st.markdown("**Topics**:")
                    st.markdown(", ".join(f"`{topic}`" for topic in details['topics']))
                
                # Display similar questions if available
                if hasattr(st.session_state.current_question, 'similar_questions') and \
                   st.session_state.current_question.similar_questions:
                    st.markdown("### Similar Problems")
                    for question in st.session_state.current_question.similar_questions:
                        difficulty_color = {
                            'Easy': 'green',
                            'Medium': 'orange',
                            'Hard': 'red'
                        }.get(question['difficulty'], 'grey')
                        
                        st.markdown(
                            f"- {question['title']} "
                            f"<span style='color: {difficulty_color}'>"
                            f"({question['difficulty']})</span>",
                            unsafe_allow_html=True
                        )

def display_full_problem_description(expanded=False):
    """Display full problem description with images"""
    if st.session_state.current_question:
        with st.expander("Full Problem Description", expanded=expanded):
            # Check if current_question is LeetCodeQuestion object
            if hasattr(st.session_state.current_question, 'get_formatted_description'):
                description = st.session_state.current_question.get_formatted_description()
            else:
                # Fallback to stored question text
                description = st.session_state.current_question.question_text
            
            st.markdown(description)
            
            

def save_current_chat():
    """Save current chat to database"""
    if not (st.session_state.messages and st.session_state.current_problem):
        return

    # Check if last message is from assistant
    if st.session_state.messages[-1]['role'] != 'assistant':
        return

    db_handler = st.session_state.db_handler
    current_question = st.session_state.current_question

    chat_data = {
        'timestamp': datetime.now(),
        'problem_url': st.session_state.current_problem,
        'problem_title': current_question.title,
        'difficulty': current_question.difficulty,
        'messages': st.session_state.messages,
        'proficiency_level': st.session_state.proficiency_level,
        'problem_details': {
            'title': current_question.title,
            'difficulty': current_question.difficulty,
            'topics': current_question.topic_tags,
            'question_text': current_question.question_text,
            'images': current_question.images if hasattr(current_question, 'images') else [],
            'examples': current_question.examples if hasattr(current_question, 'examples') else [],
            'raw_html': current_question.raw_html if hasattr(current_question, 'raw_html') else ''
        },
        'summary': db_handler.generate_chat_summary(st.session_state.messages)
    }

    db_handler.save_chat(chat_data)

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
        
        # Clear chat button at the top
        if st.button("New Discussion 🆕"):
            clear_chat_history()
        
        # DSA Proficiency Selector
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
        
        # LeetCode URL input
        with st.expander("🔗 Problem URL", expanded=True):
            # Use the session state value if available
            default_url = st.session_state.get('leetcode_url_input', '')
            leetcode_url = st.text_input(
                "Enter LeetCode Problem URL:",
                value=default_url,
                key="leetcode_url_field",
                help="Paste the URL of the problem you need help with"
            )
            
            # Process URL input
            if leetcode_url:
                process_leetcode_url(leetcode_url)
        
        # Render chat history
        render_chat_history_sidebar(st.session_state.db_handler)
        
        # Display problem details (in sidebar)
        display_full_problem_description(expanded=True)
        display_problem_details()
       
    
    display_full_problem_description()

    # Display current problem if exists
    if st.session_state.current_problem:
        st.success(f"Currently discussing: {st.session_state.current_question.title}")
    
    # Save chat when problem changes
    if st.session_state.messages and st.session_state.current_problem:
        save_current_chat()

    # Display proficiency level if set
    if st.session_state.proficiency_level:
        st.info(f"Providing help suitable for {st.session_state.proficiency_level.split('(')[0].strip()} level")
    
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input handling
    if prompt := st.chat_input("Ask your doubt here..."):
        if not st.session_state.current_problem:
            st.warning("Please enter a LeetCode problem URL first!")
            return
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
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
                # Save chat only after assistant response
                save_current_chat()

if __name__ == "__main__":
    main()