from typing import Any, Callable, Dict

import streamlit as st
from config.settings import Config
from database.chat_manager import ChatManager


class Sidebar:
    """Handles the rendering of the sidebar components."""

    def __init__(self, state: Dict[str, Any], chat_manager: ChatManager):
        """Initializes the Sidebar with the current Streamlit session state and a ChatManager."""
        self.state = state
        self.chat_manager = chat_manager

    def render(self, new_chat_callback: Callable, proficiency_change_callback: Callable,
               url_submit_callback: Callable, load_chat_callback: Callable,
               delete_chat_callback: Callable) -> None:
        """Renders the sidebar components."""
        with st.sidebar:
            st.header("Configuration ⚙️")

            self._render_new_chat_button(new_chat_callback)
            self._render_proficiency_selector(proficiency_change_callback)
            self._render_problem_input(url_submit_callback)
            self._render_previous_discussions(load_chat_callback, delete_chat_callback)

    def _render_new_chat_button(self, new_chat_callback: Callable) -> None:
        """Renders the 'New Discussion' button."""
        if st.button("New Discussion 🆕"):
            new_chat_callback()

    def _render_proficiency_selector(self, proficiency_change_callback: Callable) -> None:
        """Renders the proficiency level selector."""
        with st.expander("🎯 Proficiency Level", expanded=True):
            proficiency_level = st.radio(
                "Select your DSA proficiency level:",
                options=Config.PROFICIENCY_LEVELS,
                help="This helps me adjust my explanations to your level",
                index=self._get_proficiency_index(),
                on_change=proficiency_change_callback
            )
            st.session_state.proficiency_level = proficiency_level

    def _get_proficiency_index(self) -> int:
        """Gets the index of the current proficiency level, defaults to Intermediate if not found."""
        try:
            return Config.PROFICIENCY_LEVELS.index(
                self.state.get("proficiency_level", Config.DEFAULT_PROFICIENCY)
            )
        except ValueError:
            return Config.PROFICIENCY_LEVELS.index(Config.DEFAULT_PROFICIENCY)  # Default to "Intermediate"

    def _render_problem_input(self, url_submit_callback: Callable) -> None:
        """Renders the problem URL input field."""
        with st.expander("🔗 Problem URL", expanded=True):
            default_url = self.state.get("leetcode_url_input", "")
            leetcode_url = st.text_input(
                "Enter LeetCode Problem URL:",
                value=default_url,
                key="leetcode_url_field",
                help="Paste the URL of the problem you need help with",
                on_change=url_submit_callback,
            )

            print(f"User entered URL: {leetcode_url}")  # Debug to see if the URL is captured

            # Ensure the URL is being stored in session state
            st.session_state.leetcode_url_input = leetcode_url
            st.session_state.current_problem = leetcode_url


    def _render_previous_discussions(self, load_chat_callback: Callable,
                                      delete_chat_callback: Callable) -> None:
        """Renders the previous discussions section with load and delete buttons."""
        with st.expander("📚 Previous Discussions", expanded=False):
            recent_chats = self.chat_manager.get_chat_history()
            if not recent_chats:
                st.info("No previous chats found")
                return

            for chat in recent_chats:
                chat_id = str(chat["_id"])
                st.markdown(f"#### 📝 {chat['problem_details']['title']}")

                # Render additional details
                metadata_str = (
                    f"**Difficulty**: {chat['problem_details']['difficulty']} • "
                    f"**Questions**: {len(chat['messages']) // 2}"
                )
                st.markdown(metadata_str)

                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("Load Chat", key=f"load_{chat_id}"):
                        load_chat_callback(chat)
                with col2:
                    if st.button("Delete", key=f"delete_{chat_id}"):
                        delete_chat_callback(chat_id)
                st.divider()
