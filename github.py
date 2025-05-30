from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize FastMCP server
github_mcp = FastMCP("github")

GITHUB_API_BASE = "https://api.github.com"
USER_AGENT = "github-tool/1.0"

async def make_github_request(url: str, params: dict[str, Any] = {}) -> dict[str, Any] | list[Any] | None:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github.v3+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"GitHub API call failed: {e}")
            return None

# Tool: List public repos for a given username
@github_mcp.tool()
async def list_public_repos(username: str) -> str:
    """List public repositories for a GitHub username.

    Args:
        username: GitHub username(e.g., 'octocat')
    """
    url = f"{GITHUB_API_BASE}/users/{username}/repos"
    data = await make_github_request(url)

    if not data or not isinstance(data, list):
        return f"Unable to fetch repositories for user '{username}'."

    if not data:
        return f"No public repositories found for user '{username}'."

    repos = [repo["name"] for repo in data]
    return "\n".join(repos)

@github_mcp.tool()
async def list_issues(username: str, repo: str, state: str = "open") -> str:
    """List issues for a specific GitHub repository.

    Args:
        username: GitHub username or organization (e.g., 'guptarajiv535')
        repo: Repository name (e.g., 'sample-repo')
        state: State of issues to list ('open', 'closed', 'all')
    """
    print(f"Fetching {state} issues for {username}/{repo}")
    url = f"{GITHUB_API_BASE}/repos/{username}/{repo}/issues"
    data = await make_github_request(url, params={"state": state})

    if not data or not isinstance(data, list):
        return f"Unable to fetch issues for '{username}/{repo}'."

    issues = [f"- #{issue['number']}: {issue['title']}" for issue in data if 'pull_request' not in issue]
    return "\n".join(issues) if issues else f"No {state} issues found in '{username}/{repo}'."

@github_mcp.tool()
async def create_github_issue(username: str, repo: str, title: str, body: str) -> str:
    """Create a GitHub issue in a specified repository.

    Args:
        username: GitHub username or organization (e.g., 'guptarajiv535')
        repo: Repository name (e.g., 'sample-repo')
        title: Issue title
        body: Issue body
    """
    token = os.getenv("GITHUB_TOKEN", "").strip()
    print(f"Using GitHub token: {token[:4]}...***")  # Debug only

    if not token:
        return "GitHub token not set in environment variable 'GITHUB_TOKEN'."

    url = f"{GITHUB_API_BASE}/repos/{username}/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "title": title,
        "body": body,
        "labels": ["bug"]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            issue = response.json()
            return f"Issue created: #{issue['number']} - {issue['title']} → {issue['html_url']}"
        except Exception as e:
            return f"Failed to create issue: {e}"    

if __name__ == "__main__":
    # Initialize and run the server
    print("Starting GitHub MCP server...")
    github_mcp.run(transport='stdio') 