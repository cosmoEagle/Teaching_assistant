from typing import Dict, List

import google.generativeai as genai
from config.settings import Config
from prompts import get_system_prompt

class TeachingAssistant:
    """
    AI Teaching Assistant agent responsible for generating responses
    and maintaining conversation context.
    """

    def __init__(self):
        """Initialize the teaching assistant with API configuration"""
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def _create_prompt(self, question: str, problem_url: str,
                      chat_history: List[Dict], proficiency: str) -> str:
        """
        Create a context-aware prompt for the AI.

        Args:
            question: User's current question
            problem_url: LeetCode problem URL
            chat_history: Previous conversation history
            proficiency: User's proficiency level

        Returns:
            Formatted prompt string
        """
        return get_system_prompt(question, problem_url, chat_history, proficiency)
    
    async def get_response(self, question: str, problem_url: str,
                          chat_history: List[Dict], proficiency: str) -> str:
        """
        Generate an AI response based on the user's question and context.

        Args:
            question: User's current question
            problem_url: LeetCode problem URL
            chat_history: Previous conversation history
            proficiency: User's proficiency level

        Returns:
            AI-generated response
        """
        prompt = self._create_prompt(question, problem_url, chat_history, proficiency)
        response = await self.model.generate_content_async(prompt)
        return response.text
