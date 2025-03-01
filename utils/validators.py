import re


def is_valid_leetcode_url(url: str) -> bool:
    """
    Check if a string is a valid LeetCode URL.

    Args:
        url (str): The string to check.

    Returns:
        bool: True if the string is a valid LeetCode URL, False otherwise.
    """
    pattern = re.compile(r"^(https?://)?(www\.)?leetcode\.com/problems/[\w-]+/?$")
    return bool(pattern.match(url))
