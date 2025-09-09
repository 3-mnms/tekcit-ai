from fastapi import APIRouter
from pydantic import BaseModel
from review_ai.review_analyze import review_analyze

router = APIRouter()

class ReviewRequest(BaseModel):
    summary: str
    new_review: str
    p_count: int
    neg_count: int
    neu_count: int

@router.post("/review/analyze")
async def analyze_review(request: ReviewRequest):
    summary = request.summary
    new_review = request.new_review
    p_count = request.p_count
    neg_count = request.neg_count
    neu_count = request.neu_count

    result = review_analyze(summary, new_review, p_count, neg_count, neu_count)
    return result
