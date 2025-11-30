import requests
import base64
from typing import Dict, Any, List, Optional
from config import Config

class GitHubClient:
    """GitHub API client for PR operations"""
    
    def __init__(self):
        self.token = Config.GITHUB_TOKEN
        self.repo = Config.GITHUB_REPO
        self.base_url = f"https://api.github.com/repos/{self.repo}"
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }

    # ---------- FIXED / RESTORED ----------
    def get_pr_details(self, pr_number: int) -> Dict[str, Any]:
        """Get PR metadata and details"""
        url = f"{self.base_url}/pulls/{pr_number}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # ---------- FIXED: only ONE get_pr_files ----------
    def get_pr_files(self, pr_number: int) -> List[Dict[str, Any]]:
        """Get list of files changed in PR"""
        url = f"{self.base_url}/pulls/{pr_number}/files"
        
        # use normal Accept so JSON is returned
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_file_content(self, file_path: str, ref: str) -> Optional[str]:
        """Get file content from repository"""
        url = f"{self.base_url}/contents/{file_path}?ref={ref}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        content_data = response.json()

        if content_data.get('encoding') == 'base64':
            return base64.b64decode(content_data['content']).decode('utf-8')

        return content_data.get('content', '')

    def get_pr_comments(self, pr_number: int) -> List[Dict[str, Any]]:
        """Get all comments on a PR"""
        url = f"{self.base_url}/issues/{pr_number}/comments"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_comment(self, pr_number: int, body: str):
        """Create a comment on a PR"""
        url = f"{self.base_url}/issues/{pr_number}/comments"
        response = requests.post(url, headers=self.headers, json={'body': body})
        response.raise_for_status()
        return response.json()

    def add_labels(self, pr_number: int, labels: List[str]):
        """Add labels to a PR"""
        url = f"{self.base_url}/issues/{pr_number}/labels"
        response = requests.post(url, headers=self.headers, json={'labels': labels})
        response.raise_for_status()
        return response.json()
