from typing import Dict, Any
from db import Database

class EarlyPolicyAgent:
    """Checks basic PR issues and policies"""
    
    def __init__(self):
        self.db = Database()
    
    def run(self, pr_number: int) -> Dict[str, Any]:
        """Execute early policy checks"""
        print(f"Running Early Policy Agent for PR #{pr_number}")
        
        # Get ingestion data
        pr_data = self.db.get_agent_output(pr_number, 'ingestion_agent')
        if not pr_data:
            raise ValueError("No ingestion data found")
        
        issues = []
        warnings = []
        
        # Check for missing description
        description = pr_data.get('description', '').strip()
        if not description or len(description) < 10:
            issues.append("PR description is missing or too short")
        
        # Check base branch
        base_branch = pr_data.get('base_branch', '')
        if base_branch not in ['main', 'master', 'develop']:
            warnings.append(f"Unconventional base branch: {base_branch}")
        
        # Check diff size
        total_changes = 0
        for file in pr_data.get('changed_files', []):
            total_changes += file.get('changes', 0)
        
        if total_changes > 1000:
            issues.append(f"PR is too large ({total_changes} changes). Consider breaking it down.")
        elif total_changes > 500:
            warnings.append(f"Large PR ({total_changes} changes). Review may take longer.")
        
        # Check number of files
        num_files = len(pr_data.get('changed_files', []))
        if num_files > 50:
            issues.append(f"Too many files changed ({num_files}). Consider smaller scope.")
        
        result = {
            'issues_found': issues,
            'warnings': warnings,
            'total_changes': total_changes,
            'num_files': num_files,
            'has_description': bool(description and len(description) >= 10),
            'base_branch_approved': base_branch in ['main', 'master', 'develop']
        }
        
        # Save to database
        self.db.save_agent_output(pr_number, 'early_policy_agent', result)
        
        return result