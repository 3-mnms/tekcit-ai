from pydantic import BaseModel

class KakaoResponse(BaseModel):
    place_name: str
    address_name: str
    x: str
    y: str