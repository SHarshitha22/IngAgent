import time
from typing import Optional, Dict, Any
from github_client import GitHubClient
from config import Config
from db import Database

class ApprovalSystem:
    """Handles approval polling and decision making"""
    
    def __init__(self):
        self.github_client = GitHubClient()
        self.db = Database()
    
    def wait_for_approval(self, pr_number: int, approval_step: int, 
                         expected_command: str) -> bool:
        """
        Poll for approval command and return decision
        Returns True if approved, False if rejected
        """
        print(f"Waiting for approval step {approval_step} on PR #{pr_number}")
        
        for attempt in range(Config.MAX_POLL_ATTEMPTS):
            print(f"Polling attempt {attempt + 1}/{Config.MAX_POLL_ATTEMPTS}")
            
            # Check for existing approval in database
            existing_approval = self.db.get_approval(pr_number, approval_step)
            if existing_approval:
                return existing_approval['approved']
            
            # Check for new comments
            comments = self.github_client.get_pr_comments(pr_number)
            latest_decision = self._check_comments_for_approval(
                comments, expected_command, pr_number, approval_step
            )
            
            if latest_decision is not None:
                return latest_decision
            
            # Wait before next poll
            time.sleep(Config.POLL_INTERVAL_SECONDS)
        
        # Timeout - treat as rejection
        self.db.save_approval(pr_number, approval_step, False, 
                             "system", "Approval timeout")
        return False
    
    def _check_comments_for_approval(self, comments: List[Dict[str, Any]], 
                                   expected_command: str, pr_number: int, 
                                   approval_step: int) -> Optional[bool]:
        """Check comments for approval/rejection commands"""
        for comment in reversed(comments):  # Check newest first
            body = comment.get('body', '').strip().lower()
            author = comment.get('user', {}).get('login', '')
            
            if expected_command.lower() in body:
                if '/approve-step' in body:
                    self.db.save_approval(pr_number, approval_step, True, 
                                         author, comment.get('body'))
                    return True
                elif '/reject-step' in body:
                    self.db.save_approval(pr_number, approval_step, False, 
                                         author, comment.get('body'))
                    return False
        
        return None