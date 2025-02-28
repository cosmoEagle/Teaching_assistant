import google.generativeai as genai
import os
from dotenv import load_dotenv
from .prompts import get_system_prompt, get_proficiency_guidelines
from .leetcode_api import fetch_leetcode_question

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')

def get_gemini_response_stream(user_prompt, leetcode_url, conversation_history, proficiency_level):
    """Get streaming response from Gemini with context management"""
    
    # Fetch question context
    question = fetch_leetcode_question(leetcode_url)
    if not question:
        return "Sorry, I couldn't fetch the question details. Please check the URL and try again."
    
    # Get system prompt and proficiency guidelines
    system_prompt = get_system_prompt(leetcode_url, proficiency_level)
    guidelines = get_proficiency_guidelines(proficiency_level)
    
    # Construct context from conversation history
    context = "\n".join([
        f"{msg['role']}: {msg['content']}" 
        for msg in conversation_history[-5:]
    ])
    
    # Construct the prompt
    prompt_text = f"""
    {system_prompt}

    PROBLEM CONTEXT:
    {question.get_formatted_context()}

    STUDENT INFORMATION:
    Proficiency Level: {proficiency_level}
    
    CONVERSATION HISTORY:
    {context}
    
    CURRENT QUESTION:
    {user_prompt}
    
    RESPONSE GUIDELINES:
    {guidelines}
    
    Additional Instructions:
    1. Use the problem details provided above to give accurate guidance
    2. Consider the problem's difficulty ({question.difficulty}) when providing hints
    3. Reference relevant topics: {', '.join(question.topic_tags)}
    4. Don't provide direct solutions
    5. Use code blocks for any code snippets (wrapped in ```)
    6. Use mathematical notation when needed (wrapped in $ or $$)
    
    Your response:
    """
    
    try:
        response = model.generate_content(
            prompt_text,
            stream=True,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40
            }
        )
        return response
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"