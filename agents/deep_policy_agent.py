from typing import Dict, Any, List
from db import Database
from config import Config
import requests
import re

class DeepPolicyAgent:
    """Enforces coding standards, documentation, naming, security, and test expectations"""
    
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
        """Enforce deep policy checks"""
        print(f"Running Deep Policy Agent for PR #{pr_number}")
        
        # Get ingestion data
        pr_data = self.db.get_agent_output(pr_number, 'ingestion_agent')
        if not pr_data:
            raise ValueError("No ingestion data found")
        
        # Get reviewer findings
        review_data = self.db.get_agent_output(pr_number, 'reviewer_agent')
        
        # Analyze code standards
        policy_violations = []
        standards_met = []
        
        # Check file types and patterns
        for file in pr_data.get('changed_files', []):
            filename = file.get('filename', '')
            
            # Check for documentation in new files
            if self._is_source_file(filename) and not self._has_test_file(filename, pr_data):
                policy_violations.append(f"Missing test file for: {filename}")
            
            # Check naming conventions
            if not self._check_naming_conventions(filename):
                policy_violations.append(f"Poor naming convention: {filename}")
        
        # Use LLM for deeper policy analysis
        prompt = f"""
        Analyze this PR for compliance with software engineering standards:
        
        PR: {pr_data.get('title', 'N/A')}
        Files Changed: {[f['filename'] for f in pr_data.get('changed_files', [])]}
        
        Review Findings: {review_data.get('review_findings', 'N/A') if review_data else 'N/A'}
        
        Check for:
        1. Documentation standards (comments, README updates)
        2. Code organization and structure
        3. Security best practices
        4. Test coverage expectations
        5. Error handling patterns
        6. Dependency management
        7. Configuration changes
        
        List specific policy violations or compliance issues.
        """
        
        try:
            policy_analysis = self._call_llm(prompt)
            
            # Parse LLM response for violations
            if "violation" in policy_analysis.lower() or "issue" in policy_analysis.lower():
                policy_violations.extend([
                    line.strip() for line in policy_analysis.split('\n') 
                    if line.strip() and not line.strip().startswith('#')
                ])
            
            result = {
                'policy_violations': policy_violations,
                'standards_met': standards_met,
                'llm_analysis': policy_analysis,
                'files_checked': len(pr_data.get('changed_files', [])),
                'analysis_success': True
            }
        except Exception as e:
            result = {
                'policy_violations': policy_violations,
                'standards_met': standards_met,
                'llm_analysis': f"Failed LLM analysis: {str(e)}",
                'files_checked': len(pr_data.get('changed_files', [])),
                'analysis_success': False,
                'error': str(e)
            }
        
        # Save to database
        self.db.save_agent_output(pr_number, 'deep_policy_agent', result)
        
        return result
    
    def _is_source_file(self, filename: str) -> bool:
        """Check if file is a source code file"""
        source_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']
        return any(filename.endswith(ext) for ext in source_extensions)
    
    def _has_test_file(self, filename: str, pr_data: Dict[str, Any]) -> bool:
        """Check if corresponding test file exists in changes"""
        test_patterns = ['test_', '_test.', 'spec.', 'test/']
        changed_files = [f['filename'] for f in pr_data.get('changed_files', [])]
        
        for test_file in changed_files:
            if any(pattern in test_file for pattern in test_patterns):
                return True
        return False
    
    def _check_naming_conventions(self, filename: str) -> bool:
        """Check filename follows conventions"""
        # Basic check for snake_case or kebab-case
        if '_' in filename or '-' in filename:
            return True
        return not any(c.isupper() for c in filename if c.isalpha())