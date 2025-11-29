from typing import Dict, Any
from db import Database
from approval import ApprovalSystem

class ApprovalAgent2:
    """Second approval step - pauses pipeline for final human review"""
    
    def __init__(self):
        self.db = Database()
        self.approval_system = ApprovalSystem()
    
    def run(self, pr_number: int) -> Dict[str, Any]:
        """Execute second approval step"""
        print(f"Running Approval Agent #2 for PR #{pr_number}")
        
        # Wait for human approval
        approved = self.approval_system.wait_for_approval(
            pr_number, 8, "/approve-step 8"
        )
        
        result = {
            'approved': approved,
            'step': 8,
            'timestamp': 'completed'
        }
        
        if not approved:
            # Halt pipeline
            self.db.halt_pipeline(pr_number, 'approval_agent_2', 'Step 8 rejected')
            result['pipeline_status'] = 'halted'
        else:
            result['pipeline_status'] = 'continuing'
        
        return result