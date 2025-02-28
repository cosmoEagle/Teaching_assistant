import requests
from typing import Dict, Optional
import json
from bs4 import BeautifulSoup

class LeetCodeQuestion:
    def __init__(self, data: Dict):
        self.title = data.get('questionTitle', '')
        self.difficulty = data.get('difficulty', '')
        self.question_text = self._clean_html(data.get('question', ''))
        self.topic_tags = [tag['name'] for tag in data.get('topicTags', [])]
        self.examples = data.get('exampleTestcases', '').split('\n')
        self.similar_questions = self._parse_similar_questions(data.get('similarQuestions', ''))
        self.question_id = data.get('questionFrontendId', '')
        self.link = data.get('link', '')

    def _clean_html(self, html_content: str) -> str:
        """Convert HTML to clean text"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Convert tables to markdown format
        for table in soup.find_all('table'):
            markdown_table = self._convert_table_to_markdown(table)
            table.replace_with(soup.new_string(markdown_table))
        
        # Get clean text
        text = soup.get_text()
        return text.strip()

    def _convert_table_to_markdown(self, table) -> str:
        """Convert HTML table to markdown format"""
        markdown = []
        
        # Process headers
        headers = []
        for th in table.find_all('th'):
            headers.append(th.get_text().strip())
        markdown.append('| ' + ' | '.join(headers) + ' |')
        markdown.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
        
        # Process rows
        for row in table.find_all('tr')[1:]:  # Skip header row
            cols = []
            for td in row.find_all('td'):
                cols.append(td.get_text().strip())
            markdown.append('| ' + ' | '.join(cols) + ' |')
        
        return '\n'.join(markdown)

    def _parse_similar_questions(self, similar_questions_str: str) -> list:
        """Parse similar questions JSON string"""
        try:
            questions = json.loads(similar_questions_str)
            return [
                {
                    'title': q['title'],
                    'difficulty': q['difficulty']
                }
                for q in questions
            ]
        except:
            return []

    def get_formatted_context(self) -> str:
        """Return formatted context for the LLM"""
        context = f"""
Problem: {self.title} (LC{self.question_id})
Difficulty: {self.difficulty}
Topics: {', '.join(self.topic_tags)}

Problem Description:
{self.question_text}

Examples:
{self._format_examples()}

Related Topics: {', '.join(self.topic_tags)}
Similar Questions: {self._format_similar_questions()}
        """
        return context.strip()

    def _format_examples(self) -> str:
        """Format example test cases"""
        return '\n'.join([f"Example {i+1}: {example}" 
                         for i, example in enumerate(self.examples)])

    def _format_similar_questions(self) -> str:
        """Format similar questions"""
        if not self.similar_questions:
            return "None"
        return ', '.join([
            f"{q['title']} ({q['difficulty']})"
            for q in self.similar_questions
        ])

def fetch_leetcode_question(leetcode_url: str) -> Optional[LeetCodeQuestion]:
    """Fetch question data from API"""
    try:
        # Extract title slug from LeetCode URL
        title_slug = leetcode_url.split('problems/')[1].rstrip('/')
        
        # Construct API URL
        api_url = f"https://alfa-leetcode-api.onrender.com/select?titleSlug={title_slug}"
        
        # Fetch data
        response = requests.get(api_url)
        response.raise_for_status()
        
        # Parse response
        question_data = response.json()
        return LeetCodeQuestion(question_data)
        
    except Exception as e:
        print(f"Error fetching question: {e}")
        return None