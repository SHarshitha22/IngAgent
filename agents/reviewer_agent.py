from typing import Dict, Any
from db import Database
from config import Config
import requests
import json

class ReviewerAgent:
    """Performs deep code review for logic issues, bugs, and code smells"""
    
    def __init__(self):
        self.db = Database()
        self.llm_config = Config.get_llm_config()
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with given prompt"""
        headers = {
            'Authorization': f'Bearer {self.llm_config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.llm_config['model'],
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': self.llm_config['temperature']
        }
        
        base_url = 'https://api.openai.com/v1'
        if 'base_url' in self.llm_config:
            base_url = self.llm_config['base_url']
        
        response = requests.post(f'{base_url}/chat/completions', 
                               headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
    
    def run(self, pr_number: int) -> Dict[str, Any]:
        """Perform deep code review"""
        print(f"Running Reviewer Agent for PR #{pr_number}")
        
        # Get ingestion data
        pr_data = self.db.get_agent_output(pr_number, 'ingestion_agent')
        if not pr_data:
            raise ValueError("No ingestion data found")
        
        # Prepare code context for review
        code_context = ""
        for file in pr_data.get('changed_files', []):
            filename = file.get('filename', '')
            patch = file.get('patch', '')[:2000]  # Limit size
            code_context += f"File: {filename}\nChanges:\n{patch}\n\n"
        
        prompt = f"""
        Perform a thorough code review for the following pull request:
        
        Title: {pr_data.get('title', 'N/A')}
        Description: {pr_data.get('description', 'N/A')}
        
        Code Changes:
        {code_context}
        
        Please analyze for:
        1. Logic errors or bugs
        2. Code smells and anti-patterns
        3. Performance issues
        4. Security vulnerabilities
        5. Maintainability concerns
        6. Edge cases not handled
        
        Provide specific, actionable feedback. Format your response as:
        - **Critical Issues**: [list any critical problems]
        - **Suggestions**: [list improvement suggestions]
        - **Questions**: [any clarifying questions about the implementation]
        
        Be constructive and technical in your review.
        """
        
        try:
            review = self._call_llm(prompt)
            
            result = {
                'review_findings': review,
                'files_reviewed': len(pr_data.get('changed_files', [])),
                'review_success': True,
                'review_categories': ['logic', 'bugs', 'smells', 'performance', 'security']
            }
        except Exception as e:
            result = {
                'review_findings': f"Failed to generate review: {str(e)}",
                'files_reviewed': len(pr_data.get('changed_files', [])),
                'review_success': False,
                'error': str(e)
            }
        
        # Save to database
        self.db.save_agent_output(pr_number, 'reviewer_agent', result)
        
        return result