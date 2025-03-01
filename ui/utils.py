import streamlit as st


def display_problem_details(problem_details):
    """Display problem details in a formatted way."""

    if not problem_details:
        st.warning("No problem details available.")
        return

    st.write(f"**Title**: {problem_details.get('title', 'N/A')}")
    st.write(f"**Difficulty**: {problem_details.get('difficulty', 'N/A')}")
    topics = problem_details.get("topics")
    if topics:
        st.write(f"**Topics**: {', '.join(topics)}")
    else:
        st.write("No topics available for this problem.")


def display_chat_message(role, content):
    """Display a chat message in the Streamlit app."""
    with st.chat_message(role):
        st.markdown(content)


def clear_chat_messages():
    """Clear all chat messages from the session state."""
    st.session_state.messages = []


def load_chat_from_database(chat_id, chat_manager, state):
    """Load chat from database and update session state."""
    chat = chat_manager.get_chat_by_id(chat_id)
    if chat:
        state.messages = chat.messages
        state.current_problem = chat.problem_url
        state.problem_details = chat.problem_details
        state.proficiency_level = chat.proficiency_level
        st.success(f"Loaded chat session from {chat.timestamp}")
    else:
        st.error("Chat session not found in database.")
