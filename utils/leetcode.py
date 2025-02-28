import re

def validate_leetcode_url(url):
    """Validate if the given URL is a valid LeetCode problem URL"""
    leetcode_pattern = r'^https?://leetcode\.com/problems/[a-zA-Z0-9-]+/?$'
    return bool(re.match(leetcode_pattern, url))