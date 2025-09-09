from fastapi import APIRouter
from pydantic import BaseModel
from activity_ai.recommend_activity import recommend_activity
from typing import List
from activity_ai.server.schemas import KakaoResponse
router = APIRouter()

class ActivityRequest(BaseModel):
    restaurants:List[KakaoResponse]
    hot_places:List[KakaoResponse]

@router.post("/recommend")
async def activity_ai_recommend(request: ActivityRequest):
    restaurants = request.restaurants
    hot_places = request.hot_places

    result = recommend_activity(restaurants, hot_places)
    return result
