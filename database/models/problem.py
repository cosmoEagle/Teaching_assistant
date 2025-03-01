from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Problem:
    """
    Represents a LeetCode problem with associated metadata.
    """

    problem_id: str
    url: str
    title: str
    difficulty: str
    content: str
    topic_tags: List[str]
    example_testcases: Optional[List[str]] = None
    images: Optional[List[Dict]] = None
    similar_questions: Optional[List[Dict]] = None