# utils/db_handler.py
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from .leetcode_api import LeetCodeQuestion
from bson.objectid import ObjectId
from functools import lru_cache

load_dotenv()


class DatabaseHandler:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['dsa_assistant']
        self.chats = self.db['chat_history']

    @lru_cache(maxsize=32)
    def get_chat_history(self, cache_key=None):
        """Get recent chat history with caching"""
        try:
            # Use the current hour as cache key to refresh periodically
            if cache_key is None:
                cache_key = datetime.now().strftime('%Y%m%d%H')
            
            return list(self.chats.find().sort('last_updated', -1).limit(10))
        except Exception as e:
            print(f"Error fetching chat history: {e}")
            return []

    def clear_cache(self):
        """Clear the chat history cache"""
        self.get_chat_history.cache_clear()

    def save_chat(self, chat_data):
        """Save chat to database"""
        try:
            # Check if chat for this problem already exists today
            existing_chat = self.chats.find_one({
                'problem_url': chat_data['problem_url'],
                'timestamp': {
                    '$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                }
            })
            
            # Add last_updated field
            chat_data['last_updated'] = datetime.now()
            
            if existing_chat:
                # Update existing chat
                self.chats.update_one(
                    {'_id': existing_chat['_id']},
                    {'$set': chat_data}
                )
                return str(existing_chat['_id'])
            else:
                # Create new chat
                result = self.chats.insert_one(chat_data)
                return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving chat: {e}")
            return None
        
    def delete_chat(self, chat_id):
        """Delete a chat by ID"""
        try:
            self.chats.delete_one({'_id': ObjectId(chat_id)})
            return True
        except Exception as e:
            print(f"Error deleting chat: {e}")
            return False
        
    def reconstruct_question_object(self, problem_details):
        """Reconstruct LeetCodeQuestion object from stored data"""
        # Create a data dictionary that matches LeetCodeQuestion's expected format
        question_data = {
            'questionTitle': problem_details['title'],
            'difficulty': problem_details['difficulty'],
            'question': problem_details.get('raw_html', ''),
            'topicTags': [{'name': topic} for topic in problem_details['topics']],
            'exampleTestcases': '\n'.join(problem_details.get('examples', [])),
        }
        return LeetCodeQuestion(question_data)
    
    

    def get_chat_by_id(self, chat_id):
        """Get specific chat by ID"""
        from bson.objectid import ObjectId
        try:
            return self.chats.find_one({'_id': ObjectId(chat_id)})
        except Exception as e:
            print(f"Error fetching chat: {e}")
            return None

    def generate_chat_summary(self, messages):
        """Generate a summary of the chat"""
        # Extract key points from the conversation
        summary = {
            'question_count': len([m for m in messages if m['role'] == 'user']),
            'last_question': next((m['content'] for m in reversed(messages) 
                                 if m['role'] == 'user'), None),
            'topics_discussed': self._extract_topics(messages)
        }
        return summary

    def _extract_topics(self, messages):
        """Extract main topics from the conversation"""
        # Simple implementation - can be enhanced with NLP
        topics = set()
        for msg in messages:
            if msg['role'] == 'assistant' and 'topics:' in msg['content'].lower():
                # Extract topics after "Topics:" keyword
                topic_text = msg['content'].lower().split('topics:')[1].split('\n')[0]
                topics.update([t.strip() for t in topic_text.split(',')])
        return list(topics)