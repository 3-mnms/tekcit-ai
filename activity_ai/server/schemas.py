from pydantic import BaseModel
from typing import List
class KakaoResponse(BaseModel):
    place_name: str
    address_name: str
    x: str
    y: str

class ActivityRequest(BaseModel):
    restaurants:List[KakaoResponse]
    hot_places:List[KakaoResponse]
