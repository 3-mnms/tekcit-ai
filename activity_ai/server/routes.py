from fastapi import APIRouter
from activity_ai.recommend_activity import recommend_activity
from activity_ai.server.schemas import ActivityRequest

router = APIRouter()

@router.post("/recommend")
async def activity_ai_recommend(request: ActivityRequest):
    restaurants = request.restaurants
    hot_places = request.hot_places

    result = recommend_activity(restaurants, hot_places)
    return result
