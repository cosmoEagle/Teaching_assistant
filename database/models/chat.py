from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Chat:
    """
    Represents a chat session with associated messages and metadata.
    """
    
    chat_id: str
    problem_url: str
    timestamp: datetime
    messages: List[Dict]
    proficiency_level: str
    problem_details: Dict
    summary: Optional[Dict] = None