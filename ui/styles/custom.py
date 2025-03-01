import streamlit as st


def apply_custom_css():
    """Apply custom CSS to Streamlit app for better aesthetics."""
    st.markdown(
        """
        <style>
            /* Overall app enhancements */
            .stApp {
                max-width: 100%;
                padding: 10px;
                background-color: #f8f9fa; /* Light gray background */
                font-family: 'Arial', sans-serif;
            }

            /* Sidebar styles */
            .stSidebar {
                background-color: #e9ecef; /* Lighter gray for sidebar */
                padding: 20px;
            }
            .stSidebar .st-bo {
                background-color: #ffffff; /* White background for elements in sidebar */
                border: 1px solid #ced4da; /* Light border for elements */
                border-radius: 0.25rem;
                padding: 10px;
                margin-bottom: 10px;
            }

            /* Header styles */
            h1 {
                color: #007bff; /* Primary blue color */
                text-align: center;
                margin-bottom: 20px;
            }

            /* Expander styles */
            .stExpander {
                border: 1px solid #ced4da;
                border-radius: 0.25rem;
                margin-bottom: 10px;
            }
            .stExpander > div[data-baseweb="expandable-header"] {
                background-color: #ffffff;
                padding: 10px;
                border-bottom: 1px solid #ced4da;
            }
            .stExpanderContent {
                padding: 10px;
            }

            /* Chat message styles */
            .stChatMessage {
                border-radius: 0.5rem;
                padding: 10px;
                margin-bottom: 10px;
            }
            .stChatMessage[data-streamlit="true"] {
                background-color: #d1ecf1; /* Cyan for user messages */
                border: 1px solid #bee5eb;
            }
            .stChatMessage[data-ai="true"] {
                background-color: #f0f0f0; /* Light gray for AI messages */
                border: 1px solid #ddd;
            }

            /* Button styles */
            .stButton>button {
                background-color: #007bff;
                color: white;
                border-radius: 0.25rem;
                padding: 0.5em 1em;
                border: none;
            }
            .stButton>button:hover {
                background-color: #0056b3;
            }

            /* Text input styles */
            .stTextInput>div>div>input {
                border: 1px solid #ced4da;
                border-radius: 0.25rem;
                padding: 0.5em;
            }

            /* Text area styles (for descriptions, etc.) */
            .stTextArea>div>div>textarea {
                border: 1px solid #ced4da;
                border-radius: 0.25rem;
                padding: 0.5em;
            }

        </style>
        """,
        unsafe_allow_html=True
    )

