# agents/ingestion_agent.py

from typing import Dict, Any, List
from github_client import GitHubClient
from db import Database

class IngestionAgent:
    """Fetches PR metadata, changed files, diffs, and stores them into SQLite"""

    def __init__(self):
        self.github_client = GitHubClient()
        self.db = Database()  # <-- matches your db.py

    def run(self, pr_number: int) -> Dict[str, Any]:
        print(f"[IngestionAgent] Running ingestion for PR #{pr_number}")

        # --- Fetch PR metadata ---
        pr_details = self.github_client.get_pr_details(pr_number)
        files = self.github_client.get_pr_files(pr_number)

        head_sha = pr_details.get("head", {}).get("sha")
        head_ref = pr_details.get("head", {}).get("ref")

        # --- Build ingestion dictionary ---
        pr_data = {
            "title": pr_details.get("title", ""),
            "description": pr_details.get("body", ""),
            "author": pr_details.get("user", {}).get("login", ""),
            "base_branch": pr_details.get("base", {}).get("ref", ""),
            "head_branch": head_ref or "",
            "head_sha": head_sha or "",
            "state": pr_details.get("state", ""),
            "created_at": pr_details.get("created_at", ""),
            "updated_at": pr_details.get("updated_at", ""),
            "changed_files": []
        }

        # --- Process changed files ---
        for f in files:
            filename = f.get("filename")
            patch = f.get("patch", "")

            # Try to fetch full file content
            content = None
            try:
                ref = head_sha or head_ref
                if filename and ref:
                    content = self.github_client.get_file_content(filename, ref)
            except Exception as e:
                print(f"[IngestionAgent] Could not fetch file content for {filename}: {e}")

            pr_data["changed_files"].append({
                "filename": filename,
                "status": f.get("status", ""),
                "additions": f.get("additions", 0),
                "deletions": f.get("deletions", 0),
                "changes": f.get("changes", 0),
                "patch": patch[:20000],  # limit stored size
                "content": content
            })

        # --- Save into SQLite using your EXACT db API ---
        self.db.save_agent_output(pr_number, "ingestion_agent", pr_data)

        print(f"[IngestionAgent] Saved ingestion output for PR #{pr_number}")

        return pr_data
