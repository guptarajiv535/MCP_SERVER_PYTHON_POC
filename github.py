from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
github_mcp = FastMCP("github")

GITHUB_API_BASE = "https://api.github.com"
USER_AGENT = "github-tool/1.0"

async def make_github_request(url: str) -> dict[str, Any] | list[Any] | None:
    """Make a request to the GitHub API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github.v3+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

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

if __name__ == "__main__":
    # Initialize and run the server
    print("Starting GitHub MCP server...")
    github_mcp.run(transport='stdio') 