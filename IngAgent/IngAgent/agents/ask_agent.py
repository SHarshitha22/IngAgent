from typing import Dict, Any, List
from db import Database
from config import Config
import requests

class AskAgent:
    """Generates clarifying questions for the PR reviewer"""
    
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
        """Generate clarifying questions"""
        print(f"Running Ask Agent for PR #{pr_number}")
        
        # Get all previous agent outputs
        ingestion_data = self.db.get_agent_output(pr_number, 'ingestion_agent')
        review_data = self.db.get_agent_output(pr_number, 'reviewer_agent')
        policy_data = self.db.get_agent_output(pr_number, 'deep_policy_agent')
        
        if not ingestion_data:
            raise ValueError("No ingestion data found")
        
        prompt = f"""
        Based on this pull request analysis, generate 3-5 clarifying questions for the author:
        
        PR Title: {ingestion_data.get('title', 'N/A')}
        PR Description: {ingestion_data.get('description', 'N/A')}
        
        Code Review Findings: {review_data.get('review_findings', 'N/A') if review_data else 'N/A'}
        Policy Violations: {policy_data.get('policy_violations', []) if policy_data else 'N/A'}
        
        Generate thoughtful, technical questions that would help clarify:
        1. Implementation decisions
        2. Design choices
        3. Edge cases
        4. Future considerations
        5. Any ambiguous parts of the code
        
        Format each question clearly and professionally.
        """
        
        try:
            questions_text = self._call_llm(prompt)
            
            # Parse questions from response
            questions = [
                q.strip() for q in questions_text.split('\n') 
                if q.strip() and (q.strip().startswith('-') or '?' in q)
            ]
            
            if not questions:
                questions = [questions_text]
            
            result = {
                'clarifying_questions': questions,
                'questions_count': len(questions),
                'generation_success': True
            }
        except Exception as e:
            result = {
                'clarifying_questions': [f"Failed to generate questions: {str(e)}"],
                'questions_count': 0,
                'generation_success': False,
                'error': str(e)
            }
        
        # Save to database
        self.db.save_agent_output(pr_number, 'ask_agent', result)
        
        return result