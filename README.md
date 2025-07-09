# DSA Teaching Assistant

This application is a **self-hosted** Streamlit-based DSA (Data Structures and Algorithms) Teaching Assistant that helps students understand and solve LeetCode problems. It leverages the Gemini API for intelligent assistance.


## 🚀 **Try the Live Demo**

<div align="center">

[![DSA Teaching Assistant](https://img.shields.io/badge/🎯_DSA_Teaching_Assistant-Demo_Only-orange?style=for-the-badge&logo=streamlit&logoColor=white)](https://huggingface.co/spaces/cosmoEagle/DSA-Teaching-Assistant)

### **[🌟 Launch Demo Application 🌟](https://huggingface.co/spaces/cosmoEagle/DSA-Teaching-Assistant)**


![Built with Streamlit](https://img.shields.io/badge/Built_with-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![LeetCode Integration](https://img.shields.io/badge/LeetCode-Integration-FFA116?style=flat-square&logo=leetcode&logoColor=white)
![Self Hosted](https://img.shields.io/badge/Deployment-Self_Hosted-blue?style=flat-square&logo=docker&logoColor=white)

</div>

> **⚠️ Demo Limitations:** 
> - The live demo is **for demonstration purposes only** with strict rate limiting
> - **Rate Limits Applied:** Maximum 10 queries per hour per device to prevent abuse
> - **First response may take 30-60 seconds** as the server needs to wake up from inactivity
> - For production use, please **self-host with your own API keys and database**


## Setup Instructions (Self-Hosting Required)

> **💡 Note:** This application is designed for self-hosting. You'll need your own API keys and database for full functionality.

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/cosmoEagle/Teaching_assistant.git
    cd Teaching_assistant
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

4.  **Set Up Environment Variables (Required):**

    * Create a `.env` file in the root directory.
    * **Get your own API keys and database:**
      * **Google API Key:** Visit [Google AI Studio](https://aistudio.google.com/) to get your Gemini API key
      * **MongoDB URI:** Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/atlas)

        ```
        GOOGLE_API_KEY=your_google_api_key_here
        MONGODB_URI=your_mongodb_uri_here
        ```

5.  **Configure Rate Limiting (Optional but Recommended):**
    
    Add these optional environment variables to control usage:
    ```
    ENABLE_RATE_LIMITING=true         # Enable/disable rate limiting
    MAX_QUERIES_PER_HOUR=50          # Default: 50 queries per hour per user
    MAX_TOKENS_PER_QUERY=4000        # Default: 4000 tokens per query
    RATE_LIMIT_STORAGE_TYPE=session  # session or database
    ```

6.  **Run the Application:**

    ```bash
    streamlit run app.py
    ```

    The application will open in your web browser with full functionality and your configured rate limits.

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
    * **Example:** `https://leetcode.com/problems/kth-largest-element-in-a-stream/`
    * ⚠️ **Note:** Use the base problem URL only (without `/description/` or other suffixes)
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

## Model Integration Details

The Gemini model integration is the heart of the DSA Teaching Assistant, enabling it to provide intelligent and context-aware assistance. Here's how it works:

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

## 🔒 Rate Limiting & Production Considerations

### ✅ Implemented Rate Limiting Features
- **✅ Configurable Limits:** Set your own query and token limits via environment variables
- **✅ Session-based Tracking:** Rate limits are applied per user session to prevent abuse
- **✅ Real-time Monitoring:** Users can see their current usage in the sidebar
- **✅ Graceful Handling:** Clear error messages when limits are exceeded
- **✅ Token Estimation:** Prevents overly long queries before API calls

### Default Rate Limits (Fully Configurable)
- **Queries per Hour:** 50 per user/device (configurable via `MAX_QUERIES_PER_HOUR`)
- **Tokens per Query:** 4,000 tokens maximum (configurable via `MAX_TOKENS_PER_QUERY`)
- **Enable/Disable:** Rate limiting can be turned on/off (via `ENABLE_RATE_LIMITING`)
- **Storage Options:** Session-based or database-based tracking

### Rate Limiting Configuration
Set these in your `.env` file:
```bash
ENABLE_RATE_LIMITING=true         # Enable rate limiting
MAX_QUERIES_PER_HOUR=50          # Queries per hour per user
MAX_TOKENS_PER_QUERY=4000        # Max tokens per single query
RATE_LIMIT_STORAGE_TYPE=session  # 'session' or 'database'
```

### Rate Limiting in Action
When rate limiting is enabled, users will see:
- **📊 Usage Limits** section in the sidebar showing current usage
- **Real-time counters** for queries used and remaining
- **Reset timer** showing when limits refresh
- **Clear error messages** when limits are exceeded
- **Helpful suggestions** to optimize query length

Example rate limit display:
```
📊 Usage Limits
Queries Used: 15/50
Remaining: 35
⏰ Rate limit resets in 45 minutes
Max tokens per query: 4000
```

### Why Self-Hosting is Recommended
- **Full Control:** Set your own rate limits and usage policies
- **Cost Management:** Use your own API quotas and manage costs directly
- **Privacy:** Your conversations and data remain on your infrastructure
- **Customization:** Modify prompts, add features, and integrate with your systems
- **No Restrictions:** Unlimited usage within your API limits

### Security Best Practices
- Store API keys in environment variables, never in code
- Use MongoDB connection strings with authentication
- Consider implementing user authentication for production deployments
- Monitor API usage to avoid unexpected costs
- Set up proper logging for debugging and monitoring