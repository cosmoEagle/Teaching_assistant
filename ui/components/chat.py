from typing import Any, Callable, Dict

import streamlit as st


class ChatInterface:
    """Handles the rendering of the chat interface."""

    def __init__(self, state: Dict[str, Any], assistant_response_callback: Callable):
        self.state = state
        self.assistant_response_callback = assistant_response_callback

    def render(self):
        """Renders the chat messages and input."""

        # Display messages from session state
        for message in self.state.get("messages", []):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle user input
        if prompt := st.chat_input("Ask your doubt here..."):
            self._handle_user_input(prompt)

    def _handle_user_input(self, prompt: str):
        """Handles user input and appends assistant response."""
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get assistant response
        response = self.assistant_response_callback(prompt)
        print(f"Assistant responded: {response}")  # Debugging log

        # Add assistant message to chat and display it
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Ensure the chat updates live in Streamlit
        st.experimental_rerun()  # This forces the UI to rerender with updated messages


class ChatMessage:
    """Represents a single chat message."""

    def __init__(self, role: str, content: str):
        """Initializes a ChatMessage."""
        self.role = role
        self.content = content

    def render(self):
        """Renders the chat message."""
        with st.chat_message(self.role):
            st.markdown(self.content)
