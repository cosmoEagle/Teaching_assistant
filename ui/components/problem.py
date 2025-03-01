from typing import Any, Dict

import streamlit as st


class ProblemDisplay:
    """Displays the problem details section in Streamlit."""

    def __init__(self, problem_details: Dict[str, Any] = None, current_question=None):
        """Initializes with problem details."""
        self.problem_details = problem_details
        self.current_question = current_question

    def render(self):
        if self.problem_details:
            self._display_main_problem_details()
        else:
            st.write("No problem details to display.")  # To debug if problem is not showing up

    def _display_main_problem_details(self):
        """Display main problem details: title, difficulty, topics."""
        with st.expander("📝 Problem Overview", expanded=False):
            difficulty_emoji = {
                "Easy": "🟢",
                "Medium": "🟡",
                "Hard": "🔴"
            }.get(self.problem_details["difficulty"], "⚪")

            st.markdown(f"### {self.problem_details['title']}")
            st.markdown(f"**Difficulty**: {difficulty_emoji} {self.problem_details['difficulty']}")
            if "topics" in self.problem_details:
                topics_md = ", ".join(f"`{topic}`" for topic in self.problem_details["topics"])
                st.markdown(f"**Topics**: {topics_md}")
            else:
                st.markdown("No topics available")

    def _display_similar_problems(self, similar_questions):
        """Display similar problems section."""
        st.markdown("### Similar Problems")
        for question in similar_questions:
            difficulty_color = {
                "Easy": "green",
                "Medium": "orange",
                "Hard": "red"
            }.get(question["difficulty"], "grey")

            st.markdown(
                f"- {question['title']} "
                f"<span style='color: {difficulty_color}'>"
                f"({question['difficulty']})</span>",
                unsafe_allow_html=True
            )


