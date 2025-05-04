# API endpoints for code review

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import openai_integration

router = APIRouter()


# Define a model for the review request
class ReviewRequest(BaseModel):
    repository: str
    pr_number: int
    code: str  # Simplified for now, will be different in a real project


@router.post("/")
async def review_code(request: ReviewRequest):
    try:
        # Generate a review using our service that wraps OpenAI API calls
        result = await openai_integration.generate_code_review(request.code)
        return {"review": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    return {"status": "ok"}
