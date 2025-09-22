from pydantic import BaseModel
from typing import List
from typing import Literal

class KakaoResponse(BaseModel):
    place_name: str
    address_name: str
    x: str
    y: str

class ActivityDTO(BaseModel):
    activity_name: str
    address_name: str
    latitude: float
    longitude: float
    activity_type: Literal["Restaurant", "HotPlace"]

class ActivityRequest(BaseModel):
    restaurants:List[KakaoResponse]
    hot_places:List[KakaoResponse]
