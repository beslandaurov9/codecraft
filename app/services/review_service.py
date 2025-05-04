import os

import httpx

from app.services.openai_integration import generate_code_review

# Load your GitHub token from env (will add it in .env or production secrets)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN is not set in environment")


async def process_pull_request(repo: str, pr_number: int):
    """
    1. Fetch PR file diffs
    2. Generate AI review
    3. Post review back to GitHub as a PR comment
    """

    # 1. Fetch the list of files changed in this PR
    files_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(files_url, headers=headers)
        resp.raise_for_status()
        files = resp.json()

    # Combine all patches into one string for review
    combined_diff = ""
    for f in files:
        # each f has keys: filename, patch, etc.
        patch = f.get("patch")
        if patch:
            combined_diff += f"### {f['filename']}\n```diff\n{patch}\n```\n\n"

    # 2. Generate review using OpenAI
    review_text = await generate_code_review(combined_diff)

    # 3. Post review back to GitHub as a comment on the PR
    comments_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    payload = {"body": review_text}
    async with httpx.AsyncClient() as client:
        resp2 = await client.post(comments_url, json=payload, headers=headers)
        resp2.raise_for_status()

    # For debugging in local logs
    print(f"Posted review comment to {repo}#{pr_number}")
