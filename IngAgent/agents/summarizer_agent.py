from typing import Dict, Any
from db import Database
from config import Config
import requests
import json

class SummarizerAgent:
    """Creates LLM-generated summary of PR changes"""
    
    def __init__(self):
        self.db = Database()
        self.llm_config = Config.get_llm_config()
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with given prompt"""
        if Config.LLM_PROVIDER == 'openai':
            return self._call_openai(prompt)
        elif Config.LLM_PROVIDER == 'llama':
            return self._call_groq(prompt)
        elif Config.LLM_PROVIDER == 'mistral':
            return self._call_mistral(prompt)
        else:
            raise ValueError(f"Unsupported LLM: {Config.LLM_PROVIDER}")
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI-compatible API"""
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
    
    def _call_groq(self, prompt: str) -> str:
        """Call Groq API for Llama"""
        return self._call_openai(prompt)  # Same interface
    
    def _call_mistral(self, prompt: str) -> str:
        """Call Mistral API"""
        return self._call_openai(prompt)  # Same interface
    
    def run(self, pr_number: int) -> Dict[str, Any]:
        """Generate PR summary"""
        print(f"Running Summarizer Agent for PR #{pr_number}")
        
        # Get ingestion data
        pr_data = self.db.get_agent_output(pr_number, 'ingestion_agent')
        if not pr_data:
            raise ValueError("No ingestion data found")
        
        # Prepare prompt for LLM
        prompt = f"""
        Please provide a concise summary of this pull request:
        
        Title: {pr_data.get('title', 'N/A')}
        Description: {pr_data.get('description', 'N/A')}
        
        Changed Files ({len(pr_data.get('changed_files', []))} files):
        {json.dumps(pr_data.get('changed_files', []), indent=2)}
        
        Please summarize:
        1. What this PR aims to accomplish
        2. Key changes made
        3. Potential impact areas
        4. Any notable patterns or concerns
        
        Keep the summary professional and technical.
        """
        
        try:
            summary = self._call_llm(prompt)
            
            result = {
                'summary': summary,
                'summary_length': len(summary),
                'files_analyzed': len(pr_data.get('changed_files', [])),
                'generation_success': True
            }
        except Exception as e:
            result = {
                'summary': f"Failed to generate summary: {str(e)}",
                'summary_length': 0,
                'files_analyzed': len(pr_data.get('changed_files', [])),
                'generation_success': False,
                'error': str(e)
            }
        
        # Save to database
        self.db.save_agent_output(pr_number, 'summarizer_agent', result)
        
        return result