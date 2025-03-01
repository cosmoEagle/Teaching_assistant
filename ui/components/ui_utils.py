import streamlit as st


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

def display_problem_details():
    """Display problem details if available"""
    if st.session_state.problem_details:
        with st.sidebar:
            with st.expander("📝 Problem Overview", expanded=False):
                details = st.session_state.problem_details
                difficulty_emoji = {'Easy': '🟢', 'Medium': '🟡', 'Hard': '🔴'}.get(details['difficulty'], '⚪')
                st.markdown(f"### {details['title']}")
                st.markdown(f"**Difficulty**: {difficulty_emoji} {details['difficulty']}")
                
                if 'topics' in details:
                    st.markdown("**Topics**:")
                    st.markdown(", ".join(f"`{topic}`" for topic in details['topics']))
                
                if hasattr(st.session_state.current_question, 'similar_questions') and \
                   st.session_state.current_question.similar_questions:
                    st.markdown("### Similar Problems")
                    for question in st.session_state.current_question.similar_questions:
                        difficulty_color = {'Easy': 'green', 'Medium': 'orange', 'Hard': 'red'}.get(question['difficulty'], 'grey')
                        st.markdown(f"- {question['title']} <span style='color: {difficulty_color}'>({question['difficulty']})</span>", unsafe_allow_html=True)

def display_full_problem_description(expanded=False):
    """Display full problem description with images"""
    if st.session_state.current_question:
        with st.expander("Full Problem Description", expanded=expanded):
            if hasattr(st.session_state.current_question, 'get_formatted_description'):
                description = st.session_state.current_question.get_formatted_description()
            else:
                description = st.session_state.current_question.question_text
            st.markdown(description)