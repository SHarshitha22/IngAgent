from github_client import GitHubClient
from agents import run_ingestion

def main():
    client = GitHubClient()
    pr = client.get_pr_details(1)   # later make dynamic
    run_ingestion(pr)

if __name__ == "__main__":
    main()

print('hello world')
# Change for PR trigger
