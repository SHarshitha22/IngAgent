print("Running ingestion agent...")
print("Hello from new branch")


from ingestion_agent import IngestionAgent

agent = IngestionAgent()

# IMPORTANT: PR number comes from GitHub
import os
pr_number = int(os.getenv("PR_NUMBER", "1"))

agent.run(pr_number)

print("Ingestion completed.")
print("How long")

