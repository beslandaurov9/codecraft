# Application entrypoint

from fastapi import FastAPI
from app.api.routes import review, webhook

app = FastAPI(
    title="CodeCraft: AI-Powered Code Review Assistant",
    description="An API to automatically review code using AI.",
    version="0.1.0"
)

# Mount the code-review endpoints under /api/review
app.include_router(review.router, prefix="/api/review")

# Mount the GitHub webhook endpoints under /webhooks
app.include_router(webhook.router, prefix="/webhooks")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
