from dataclasses import dataclass
from typing import Dict, Optional

import requests
import streamlit as st
from bs4 import BeautifulSoup


@dataclass
class LeetCodeProblem:
    """Data class for storing LeetCode problem information"""
    title: str
    difficulty: str
    question_text: str
    topic_tags: list
    images: list
    examples: list
    similar_questions: list
    question_id: str
    raw_html: str

class ProblemFetcher:
    """Agent responsible for fetching and processing LeetCode problems"""

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validating the URL is a valid LeetCode URL"""
        is_valid = "leetcode.com/problems/" in url
        print(f"URL validation: {url} is {'valid' if is_valid else 'invalid'}")  #debug
        return is_valid

    @staticmethod
    def _process_html(html_content: str) -> tuple:
        """Process HTML content and extract images and formatted text"""
        soup = BeautifulSoup(html_content, 'html.parser')
        images = []
        
        # Extract and process images
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src:
                images.append({'src': src, 'alt': alt})

        # Process text formatting
        text = ProblemFetcher._format_text(soup)
        return text, images

    @staticmethod
    def _format_text(soup: BeautifulSoup) -> str:
        """Format the problem text with proper markdown"""
        # Format code blocks
        for code in soup.find_all('code'):
            code_text = code.get_text()
            code.replace_with(f'`{code_text}`')

        # Format lists
        for ul in soup.find_all('ul'):
            items = ul.find_all('li')
            formatted_items = '\n'.join(f"- {item.get_text().strip()}" for item in items)
            ul.replace_with(soup.new_string(formatted_items))

        # Format tables
        for table in soup.find_all('table'):
            markdown_table = ProblemFetcher._convert_table_to_markdown(table)
            table.replace_with(BeautifulSoup(markdown_table, 'html.parser').new_tag('p'))  # Replace with a paragraph tag

        # Clean up extra whitespace and normalize newlines
        text = soup.get_text('\n', strip=True)
        text = '\n\n'.join(
            line.strip()
            for line in text.split('\n')
            if line.strip()
        )

        return text

    @staticmethod
    def _convert_table_to_markdown(table) -> str:
        """Convert HTML table to markdown format"""
        markdown = []
        
        # Process headers
        headers = []
        for th in table.find_all('th'):
            headers.append(th.get_text().strip())
        
        if headers:
            markdown.append('| ' + ' | '.join(headers) + ' |')
            markdown.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
        
        # Process rows
        for row in table.find_all('tr')[1:]: 
            cols = []
            for td in row.find_all('td'):
                cols.append(td.get_text().strip())
            if cols:
                markdown.append('| ' + ' | '.join(cols) + ' |')

        return '\n'.join(markdown)

    def fetch_problem(self, url: str) -> Optional[LeetCodeProblem]:
        """
        Fetch problem details from LeetCode API

        Args:
            url: LeetCode problem URL

        Returns:
            LeetCodeProblem object if successful, None otherwise
        """
        try:
            title_slug = url.split('problems/')[1].rstrip('/')
            print(f"Fetching problem for slug: {title_slug}")  
            print(f"URL being fetched: {url}")

            query = """
            query questionData($titleSlug: String!) {
              question(titleSlug: $titleSlug) {
                questionId
                title
                content
                difficulty
                exampleTestcases
                topicTags {
                  name
                }
                similarQuestions
              }
            }
            """

            variables = {"titleSlug": title_slug}
            api_url = "https://leetcode.com/graphql"

            response = requests.post(
                api_url,
                json={"query": query, "variables": variables},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            question_data = data["data"]["question"]

            # Extract information
            question_id = question_data["questionId"]
            title = question_data["title"]
            content = question_data["content"]
            difficulty = question_data["difficulty"]
            example_testcases = question_data["exampleTestcases"]
            topic_tags = [tag["name"] for tag in question_data["topicTags"]]

            # Extract similar questions
            similar_questions_json = question_data["similarQuestions"]
            similar_questions = []
            if similar_questions_json:
                try:
                    import json
                    similar_questions_list = json.loads(similar_questions_json)
                    for q in similar_questions_list:
                        similar_questions.append({
                            'title': q['title'],
                            'difficulty': q['difficulty'],
                            'titleSlug': q['titleSlug']
                        })

                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    similar_questions = []

            # Process HTML content
            question_text, images = self._process_html(content)

            # Create LeetCodeProblem instance
            problem = LeetCodeProblem(
                title=title,
                difficulty=difficulty,
                question_text=question_text,
                topic_tags=topic_tags,
                images=images,
                examples=example_testcases.split("\n"),
                similar_questions=similar_questions,
                question_id=question_id,
                raw_html=content  # Store raw HTML content
            )
            if problem:
                print("Problem successfully fetched") 
                print(f"Problem title: {problem.title}")
                print(f"Problem difficulty: {problem.difficulty}")
                print(f"Problem topics: {problem.topic_tags}")

                st.session_state.current_question = problem
                st.session_state.problem_details = {
                    'title': problem.title,
                    'difficulty': problem.difficulty,
                    'topics': problem.topic_tags
                }
            return problem

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except KeyError as e:
            print(f"KeyError: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
