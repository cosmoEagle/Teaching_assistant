# DSA Teaching Assistant

This application is a Streamlit-based DSA (Data Structures and Algorithms) Teaching Assistant that helps students understand and solve LeetCode problems. It leverages the Gemini (formerly Bard) API for intelligent assistance.

## To directly use :
[Link to Application](https://huggingface.co/spaces/cosmoEagle/DSA-Teaching-Assistant)


## Setup Instructions

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/cosmoEagle/Teaching_assistant.git
    cd dsa_assistant
    ```

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate  # On Windows
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**

    * Create a `.env` file in the root directory.
    * Add your Google API key (for Gemini)
    * Add your MongoDB URI (for saving chat history)

        ```
        GOOGLE_API_KEY=your_google_api_key
        MONGODB_URI=your_mongodb_uri
        ```

5.  **Run the Application:**

    ```bash
    streamlit run ui/streamlit_app.py
    ```

    The application will open in your web browser.

## Architecture Explanation

The application follows a modular architecture with a clear separation of concerns:

**Module Breakdown:**

* **`main.py`:**
    * Serves as the entry point for the application.
    * Initializes and orchestrates the application's components.
* **`config/`:**
    * `settings.py` manages application configurations and environment variables, ensuring secure and flexible settings management.
* **`agents/`:**
    * `teaching_assistant.py` encapsulates the AI agent's logic, handling interactions with the Gemini API and providing intelligent assistance.
    * `problem_fetcher.py` handles the fetching of LeetCode problem data from external APIs.
* **`database/`:**
    * `models/` defines data models (`chat.py`, `problem.py`) for representing chat history and LeetCode problems.
    * `chat_manager.py` manages database interactions, including saving and retrieving chat data.
* **`ui/`:**
    * `components/` contains reusable UI components (`sidebar.py`, `chat.py`, `problem.py`) for building the Streamlit interface.
    * `styles/` manages custom CSS and styling (`custom.py`) to enhance the application's visual appeal.
    * `utils.py` provides utility functions for UI-related tasks.
* **`utils/`:**
    * `leetcode_parser.py` handles the parsing of LeetCode problem descriptions, converting HTML to markdown.
    * `cache.py` provides caching utilities to improve performance by storing and retrieving frequently accessed data.
    * `validators.py` contains input validation utilities to ensure data integrity.


## How to Use the Application

1.  **Enter LeetCode URL:**
    * In the sidebar, enter the URL of the LeetCode problem you want help with.
2.  **Select Proficiency Level:**
    * Choose your DSA proficiency level to tailor the assistant's responses.
3.  **Start Chatting:**
    * Ask your questions in the chat input area.
    * The assistant will provide hints, explanations, and guidance.
4.  **View Problem Details:**
    * The problem details will be displayed in the sidebar.
5.  **View Chat History:**
    * The chat history is saved and can be viewed in the sidebar and in the main screen on top.
6.  **New Discussion:**
    * Press the "New Discussion" button to clear the current chat.
7.  **Load from history**
    * Your previous chats will be saved in your mongodb database that you can load from "Previous Discussions" expand menu and continue to chat in them.

## Gemini Integration Details

The Gemini integration is the heart of the DSA Teaching Assistant, enabling it to provide intelligent and context-aware assistance. Here's how it works:

1.  **Initialization:**
    * The `llm_handler.py` module initializes the Gemini API using the `google.generativeai` library.
    * It retrieves the API key from the `.env` file, ensuring secure access.
    * A `GenerativeModel` instance is created, specifically using the "gemini-2.0-flash" model, optimized for speed and efficiency.

2.  **Prompt Engineering:**
    * The `agents/prompts.py` module constructs a detailed prompt for each user query, leveraging several prompt optimization techniques:
        * **Role Definition:** Clearly defines Gemini's role as a DSA teaching assistant.
        * **Chain of Thought:** Encourages Gemini to reason step-by-step before responding.
        * **Contextual Information:** Includes LeetCode problem details, user proficiency, and conversation history.
        * **Task Decomposition:** Breaks down the desired behavior into clear "SHOULD" and "SHOULD NOT" instructions.
        * **Proficiency-Based Guidelines:** Tailors responses based on the student's skill level.
    * The prompt is dynamically generated, incorporating:
        * The LeetCode problem context (title, description, examples, etc.).
        * The student's proficiency level.
        * The ongoing conversation history (last 5 messages).
        * The user's current question.
        * Specific guidelines and instructions.

3.  **API Interaction:**
    * The `teaching_assistant.py` agent sends the constructed prompt to the Gemini API using the `model.get_response()` method.
    * The `question`, `problem_url`, `chat_history` and `user's proficiency` are passed as argument to generate dynamic prompt and get response.
    * Generation configurations (temperature, top\_p, top\_k) are used to control the output's creativity and diversity.

4.  **Streaming Response Handling:**
    * The `utils/stream_handler.py` module processes the streaming response:
        * It iterates through the response chunks, extracting the text.
        * It simulates a typewriter effect for a more engaging display.
        * It formats code blocks and mathematical equations for readability.
        * It handles potential errors during the streaming process.

5.  **Context Management:**
    * The application maintains a limited conversation history (last 5 messages) to provide context for subsequent queries.
    * This ensures that Gemini can understand the flow of the conversation and provide relevant responses.

6.  **Proficiency-Based Adaptation:**
    * The `agents/prompts.py` module also provides different response guidelines based on the student's proficiency level (Beginner, Intermediate, Advanced).
    * This allows Gemini to tailor its responses to the student's skill level, providing appropriate explanations and hints.