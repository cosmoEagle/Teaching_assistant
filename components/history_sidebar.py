import streamlit as st
from datetime import datetime

def render_chat_history_sidebar(db_handler):
    """Render chat history in sidebar"""
    with st.sidebar:
        with st.expander("📚 Previous Discussions", expanded=False):
            # Get recent chats with cache key
            cache_key = datetime.now().strftime('%Y%m%d%H')
            recent_chats = db_handler.get_chat_history(cache_key)
            
            if not recent_chats:
                st.info("No previous chats found")
                return

            # Pre-process chats for better performance
            today = datetime.now().date()
            today_chats = []
            earlier_chats = []
            
            # Single pass classification
            for chat in recent_chats:
                (today_chats if chat['timestamp'].date() == today else earlier_chats).append(chat)

            # Render chats using a more efficient method
            render_chat_section("Today", today_chats)
            render_chat_section("Earlier", earlier_chats)

def render_chat_section(title, chats):
    """Helper function to render a section of chats"""
    if not chats:
        return

    st.markdown(f"### {title}")
    for chat in chats:
        render_chat_item(chat)

def render_chat_item(chat):
    """Helper function to render a single chat item"""
    chat_id = str(chat['_id'])
    time_str = chat['timestamp'].strftime('%H:%M' if chat['timestamp'].date() == datetime.now().date() else '%Y-%m-%d %H:%M')
    
    st.markdown(f"#### 📝 {chat['problem_title']}")
    
    # Combine metadata into a single markdown string
    metadata = (
        f"**Time**: {time_str} • "
        f"**Difficulty**: {chat['difficulty']} • "
        f"**Questions**: {len(chat['messages'])//2}"
    )
    st.markdown(metadata)
    
    # Show topics if available
    topics = chat['summary']['topics_discussed']
    if topics:
        st.markdown("**Topics**: " + ", ".join(topics[:2]) + 
                   ("..." if len(topics) > 2 else ""))
    
    col1, col2 = st.columns([3, 2])
    with col1:
        if st.button("Load Chat", key=f"load_{chat_id}"):
            load_chat(chat)
    with col2:
        if st.button("Delete", key=f"delete_{chat_id}"):
            delete_chat(chat_id)
    st.divider()

def load_chat(chat):
    """Helper function to load a chat"""
    st.session_state.update({
        'messages': chat['messages'],
        'current_problem': chat['problem_url'],
        'problem_details': chat['problem_details'],
        'proficiency_level': chat.get('proficiency_level', 
            "Intermediate (Familiar with basic concepts)"),
        'current_question': st.session_state.db_handler.reconstruct_question_object(
            chat['problem_details']
        ),
        'leetcode_url_input': chat['problem_url'] 
    })
    st.rerun()

def delete_chat(chat_id):
    """Helper function to delete a chat"""
    st.session_state.db_handler.delete_chat(chat_id)
    st.session_state.db_handler.clear_cache()
    st.rerun()