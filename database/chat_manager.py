from datetime import datetime
from typing import Dict, List, Optional

from bson.objectid import ObjectId
from config.settings import Config
from pymongo import MongoClient, errors


class ChatManager:
    """Manager for handling chat history and database operations"""

    def __init__(self):
        """Initialize database connection"""
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client["dsa_assistant"]
            self.chats = self.db["chat_history"]
        except errors.ConnectionFailure as e:
            print(f"Connection to MongoDB failed: {e}")
            self.client = None
            self.db = None
            self.chats = None

    def save_chat(self, chat_data: Dict) -> Optional[str]:
        """
        Save or update chat history

        Args:
            chat_data: Dictionary containing chat information

        Returns:
            Chat ID if successful, None otherwise
        """
        if self.chats is None:  # Change here  if you want not connected message then copy the print
            print("Database connection is not available.")
            return None

        try:
            chat_data["last_updated"] = datetime.now()

            # Check for existing chat
            existing = self.chats.find_one({
                "problem_url": chat_data["problem_url"],
                "timestamp": {
                    "$gte": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                }
            })

            if existing:
                self.chats.update_one(
                    {"_id": existing["_id"]},
                    {"$set": chat_data}
                )
                return str(existing["_id"])
            result = self.chats.insert_one(chat_data)
            return str(result.inserted_id)
        except errors.PyMongoError as e:
            print(f"Error saving chat: {e}")
            return None

    def get_chat_history(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve recent chat history

        Args:
            limit: Maximum number of chats to retrieve

        Returns:
            List of chat history entries
        """
        if self.chats is None: # Change here if you want not connected message then copy the print
            print("Database connection is not available.")
            return []

        try:
            return list(self.chats.find().sort("last_updated", -1).limit(limit))
        except errors.PyMongoError as e:
            print(f"Error fetching chat history: {e}")
            return []

    def delete_chat(self, chat_id: str) -> bool:
        """
        Delete chat by ID

        Args:
            chat_id: ID of the chat to delete

        Returns:
            True if deletion was successful, False otherwise
        """

        if self.chats is None:
            print("Database connection is not available.")
            return False

        try:
            self.chats.delete_one({"_id": ObjectId(chat_id)})
            return True
        except errors.PyMongoError as e:
            print(f"Error deleting chat: {e}")
            return False

    def get_chat_by_id(self, chat_id: str) -> Optional[Dict]:
        """
        Retrieve specific chat by ID

        Args:
            chat_id: ID of the chat to retrieve

        Returns:
            Chat data dictionary if found, otherwise None.
        """
        if self.chats is None:
            print("Database connection is not available.")
            return None

        try:
            return self.chats.find_one({"_id": ObjectId(chat_id)})
        except errors.PyMongoError as e:
            print(f"Error fetching chat: {e}")
            return None
