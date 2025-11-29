from typing import Dict, Any
from db import Database
from approval import ApprovalSystem

class ApprovalAgent1:
    """First approval step - pauses pipeline for human review"""
    
    def __init__(self):
        self.db = Database()
        self.approval_system = ApprovalSystem()
    
    def run(self, pr_number: int) -> Dict[str, Any]:
        """Execute first approval step"""
        print(f"Running Approval Agent #1 for PR #{pr_number}")
        
        # Check early policy results
        early_policy = self.db.get_agent_output(pr_number, 'early_policy_agent')
        if not early_policy:
            raise ValueError("No early policy data found")
        
        # Wait for human approval
        approved = self.approval_system.wait_for_approval(
            pr_number, 3, "/approve-step 3"
        )
        
        result = {
            'approved': approved,
            'step': 3,
            'timestamp': 'pending' if approved is None else 'completed'
        }
        
        if not approved:
            # Halt pipeline
            self.db.halt_pipeline(pr_number, 'approval_agent_1', 'Step 3 rejected')
            result['pipeline_status'] = 'halted'
        else:
            result['pipeline_status'] = 'continuing'
        
        return result