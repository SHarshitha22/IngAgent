#!/usr/bin/env python3
import sys
import os
import argparse
from typing import Dict, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.ingestion_agent import IngestionAgent
from agents.early_policy_agent import EarlyPolicyAgent
from agents.approval_agent_1 import ApprovalAgent1
from agents.summarizer_agent import SummarizerAgent
from agents.reviewer_agent import ReviewerAgent
from agents.deep_policy_agent import DeepPolicyAgent
from agents.ask_agent import AskAgent
from agents.approval_agent_2 import ApprovalAgent2
from agents.coordinator_agent import CoordinatorAgent
from db import Database
from config import Config

class PROrchestrator:
    """Main orchestrator that runs the 9-agent pipeline in strict order"""
    
    def __init__(self):
        self.db = Database()
        self.agents = {
            'ingestion_agent': IngestionAgent(),
            'early_policy_agent': EarlyPolicyAgent(),
            'approval_agent_1': ApprovalAgent1(),
            'summarizer_agent': SummarizerAgent(),
            'reviewer_agent': ReviewerAgent(),
            'deep_policy_agent': DeepPolicyAgent(),
            'ask_agent': AskAgent(),
            'approval_agent_2': ApprovalAgent2(),
            'coordinator_agent': CoordinatorAgent()
        }
    
    def run_pipeline(self, pr_number: int) -> Dict[str, Any]:
        """Execute the 9-agent pipeline in strict sequential order"""
        print(f"🚀 Starting PR Review Pipeline for PR #{pr_number}")
        
        # Check if pipeline is already halted
        if self.db.is_pipeline_halted(pr_number):
            print("⏸️ Pipeline is halted. Exiting.")
            return {'status': 'halted'}
        
        results = {}
        
        try:
            # 1. Ingestion Agent
            print("\n" + "="*50)
            print("1. Running Ingestion Agent...")
            results['ingestion'] = self.agents['ingestion_agent'].run(pr_number)
            
            # 2. Early Policy Agent
            print("\n" + "="*50)
            print("2. Running Early Policy Agent...")
            results['early_policy'] = self.agents['early_policy_agent'].run(pr_number)
            
            # 3. Approval Agent #1
            print("\n" + "="*50)
            print("3. Running Approval Agent #1...")
            results['approval_1'] = self.agents['approval_agent_1'].run(pr_number)
            
            if not results['approval_1'].get('approved', False):
                print("❌ Pipeline halted at Approval Step 3")
                return {'status': 'halted', 'step': 3}
            
            # 4. Summarizer Agent
            print("\n" + "="*50)
            print("4. Running Summarizer Agent...")
            results['summarizer'] = self.agents['summarizer_agent'].run(pr_number)
            
            # 5. Reviewer Agent
            print("\n" + "="*50)
            print("5. Running Reviewer Agent...")
            results['reviewer'] = self.agents['reviewer_agent'].run(pr_number)
            
            # 6. Deep Policy Agent
            print("\n" + "="*50)
            print("6. Running Deep Policy Agent...")
            results['deep_policy'] = self.agents['deep_policy_agent'].run(pr_number)
            
            # 7. Ask Agent
            print("\n" + "="*50)
            print("7. Running Ask Agent...")
            results['ask'] = self.agents['ask_agent'].run(pr_number)
            
            # 8. Approval Agent #2
            print("\n" + "="*50)
            print("8. Running Approval Agent #2...")
            results['approval_2'] = self.agents['approval_agent_2'].run(pr_number)
            
            if not results['approval_2'].get('approved', False):
                print("❌ Pipeline halted at Approval Step 8")
                return {'status': 'halted', 'step': 8}
            
            # 9. Coordinator Agent
            print("\n" + "="*50)
            print("9. Running Coordinator Agent...")
            results['coordinator'] = self.agents['coordinator_agent'].run(pr_number)
            
            print("\n" + "="*50)
            print("✅ PR Review Pipeline Completed Successfully!")
            return {'status': 'completed', 'results': results}
            
        except Exception as e:
            print(f"❌ Pipeline failed with error: {str(e)}")
            return {'status': 'error', 'error': str(e)}

def main():
    parser = argparse.ArgumentParser(description='PR Review Orchestrator')
    parser.add_argument('--pr-number', type=int, required=True, help='PR number to review')
    args = parser.parse_args()
    
    orchestrator = PROrchestrator()
    result = orchestrator.run_pipeline(args.pr_number)
    
    # Exit with appropriate code
    if result['status'] == 'completed':
        sys.exit(0)
    elif result['status'] == 'halted':
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == '__main__':
    main()