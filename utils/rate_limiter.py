import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config.settings import Config
import hashlib
import json
import time


class RateLimiter:
    """Rate limiting utility for controlling API usage"""

    def __init__(self):
        self.max_queries_per_hour = Config.MAX_QUERIES_PER_HOUR
        self.max_tokens_per_query = Config.MAX_TOKENS_PER_QUERY
        self.enabled = Config.ENABLE_RATE_LIMITING

    def get_user_identifier(self) -> str:
        """Generate a unique identifier for the user session"""
        # Use session state or create a unique ID based on browser session
        if "user_id" not in st.session_state:
            # Create a unique ID based on session info and timestamp
            try:
                # Try to get some session info
                session_info = f"{time.time()}_{id(st.session_state)}"
            except:
                # Ultimate fallback
                session_info = f"user_{int(time.time() * 1000000) % 1000000}"
            st.session_state.user_id = hashlib.md5(session_info.encode()).hexdigest()[
                :16
            ]
        return st.session_state.user_id

    def get_user_queries(self) -> List[datetime]:
        """Get the list of query timestamps for the current user"""
        if not self.enabled:
            return []

        user_id = self.get_user_identifier()
        queries_key = f"rate_limit_queries_{user_id}"

        if queries_key not in st.session_state:
            st.session_state[queries_key] = []

        # Clean old queries (older than 1 hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        st.session_state[queries_key] = [
            query_time
            for query_time in st.session_state[queries_key]
            if query_time > cutoff_time
        ]

        return st.session_state[queries_key]

    def add_query_timestamp(self) -> None:
        """Add current timestamp to user's query history"""
        if not self.enabled:
            return

        user_id = self.get_user_identifier()
        queries_key = f"rate_limit_queries_{user_id}"

        if queries_key not in st.session_state:
            st.session_state[queries_key] = []

        st.session_state[queries_key].append(datetime.now())

    def check_rate_limit(self) -> Dict[str, any]:
        """
        Check if user has exceeded rate limits

        Returns:
            Dict with 'allowed' (bool), 'remaining_queries' (int),
            'reset_time' (datetime), 'message' (str)
        """
        if not self.enabled:
            return {
                "allowed": True,
                "remaining_queries": float("inf"),
                "reset_time": None,
                "message": "Rate limiting disabled",
            }

        user_queries = self.get_user_queries()
        current_queries = len(user_queries)

        if current_queries >= self.max_queries_per_hour:
            # Find the oldest query to determine reset time
            oldest_query = min(user_queries) if user_queries else datetime.now()
            reset_time = oldest_query + timedelta(hours=1)

            return {
                "allowed": False,
                "remaining_queries": 0,
                "reset_time": reset_time,
                "message": f"Rate limit exceeded. You have made {current_queries}/{self.max_queries_per_hour} queries in the last hour.",
            }

        remaining = self.max_queries_per_hour - current_queries
        next_reset = (min(user_queries) + timedelta(hours=1)) if user_queries else None

        return {
            "allowed": True,
            "remaining_queries": remaining,
            "reset_time": next_reset,
            "message": f"Queries remaining: {remaining}/{self.max_queries_per_hour}",
        }

    def check_token_limit(self, estimated_tokens: int) -> Dict[str, any]:
        """
        Check if query is within token limits

        Args:
            estimated_tokens: Estimated number of tokens for the query

        Returns:
            Dict with 'allowed' (bool) and 'message' (str)
        """
        if not self.enabled:
            return {"allowed": True, "message": "Token limiting disabled"}

        if estimated_tokens > self.max_tokens_per_query:
            return {
                "allowed": False,
                "message": f"Query too long. Estimated {estimated_tokens} tokens exceeds limit of {self.max_tokens_per_query} tokens.",
            }

        return {
            "allowed": True,
            "message": f"Token usage: {estimated_tokens}/{self.max_tokens_per_query}",
        }

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text
        Simple estimation: ~4 characters per token (rough approximation)
        """
        return len(text) // 4

    def get_rate_limit_status(self) -> Dict[str, any]:
        """Get comprehensive rate limit status for display"""
        if not self.enabled:
            return {"enabled": False, "message": "Rate limiting is disabled"}

        rate_status = self.check_rate_limit()
        user_queries = self.get_user_queries()

        return {
            "enabled": True,
            "allowed": rate_status["allowed"],
            "current_queries": len(user_queries),
            "max_queries": self.max_queries_per_hour,
            "remaining_queries": rate_status["remaining_queries"],
            "reset_time": rate_status["reset_time"],
            "max_tokens_per_query": self.max_tokens_per_query,
            "message": rate_status["message"],
        }

    def display_rate_limit_info(self) -> None:
        """Display rate limit information in the UI"""
        status = self.get_rate_limit_status()

        if not status["enabled"]:
            return

        with st.expander("📊 Usage Limits", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Queries Used",
                    f"{status['current_queries']}/{status['max_queries']}",
                )

            with col2:
                st.metric(
                    "Remaining",
                    (
                        status["remaining_queries"]
                        if status["remaining_queries"] != float("inf")
                        else "∞"
                    ),
                )

            if status["reset_time"]:
                time_until_reset = status["reset_time"] - datetime.now()
                minutes_until_reset = max(0, int(time_until_reset.total_seconds() / 60))
                st.info(f"⏰ Rate limit resets in {minutes_until_reset} minutes")

            st.caption(f"Max tokens per query: {status['max_tokens_per_query']}")

            if not status["allowed"]:
                st.error(
                    "🚫 Rate limit exceeded. Please wait before making more queries."
                )


# Global rate limiter instance
rate_limiter = RateLimiter()
