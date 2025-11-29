import os
from dotenv import load_dotenv
from github_client import GitHubClient

load_dotenv()

pr_number = int(os.getenv("PR_NUMBER", "1"))

client = GitHubClient()

pr = client.get_pr_details(pr_number)

print("PR title:", pr["title"])
print("PR author:", pr["user"]["login"])
print("PR state:", pr["state"])
