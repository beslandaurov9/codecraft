import hmac
import hashlib
import os
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from app.services.review_service import process_pull_request

load_dotenv()  # Load GITHUB_WEBHOOK_SECRET from .env
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "").encode()

def verify_signature(payload: bytes, signature_header: str) -> bool:
    """Return True if signature_header matches the HMAC-SHA256 of payload."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    received_sig = signature_header.split("=", 1)[1]
    expected_sig = hmac.new(WEBHOOK_SECRET, payload, hashlib.sha256).hexdigest()
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(received_sig, expected_sig)

router = APIRouter()

@router.post("/github")
async def handle_github_webhook(
        request: Request,
        background_tasks: BackgroundTasks
):

    # 1. Read raw body and headers
    payload = await request.body()  # Raw body bytes
    signature_header = request.headers.get("X-Hub-Signature-256")
    event_type = request.headers.get("X-GitHub-Event")

    # 2. Validate signature (uses the helper above)
    if not verify_signature(payload, signature_header):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # 3. Parse JSON safely after validation
    body = await request.json()

    # 4. Handle specific event types
    if event_type == "pull_request":
        # Extract relevant fields for code review
        pr_number = body["number"]
        repo = body["repository"]["full_name"]
        # enqueue review job
        background_tasks.add_task(process_pull_request, repo, pr_number)
        return {"status": "queued", "event": event_type}

    # 5. For any other event types - acknowledge receipt
    return {"status": "received", "event": event_type}
