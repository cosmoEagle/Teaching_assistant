from datetime import datetime
from components.db_handler import DatabaseHandler
import streamlit as st

def initialize_session_state():
    """Initialize session state"""
    if "db_handler" not in st.session_state:
        st.session_state.db_handler = DatabaseHandler()
    
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
    st.session_state.messages = []
    st.session_state.current_problem = None
    st.session_state.current_question = None
    st.session_state.problem_details = None
    st.session_state.leetcode_url_input = ''
    st.rerun()

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