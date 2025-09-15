import json
import requests
from activity_ai.config import invoke_url, headers
import re
from activity_ai.server.schemas import KakaoResponse, ActivityDTO
from typing import List

#request 정보 장소명 주소 합치기
def format_places(places: List[KakaoResponse]):
    return "\n".join([
        f"{i+1}. {p.place_name} ({p.address_name})"
        for i, p in enumerate(places)
    ])

def build_prompt(restaurants: List[KakaoResponse], hot_places: List[KakaoResponse]):
    return f"""
당신은 공연장 근처 장소 데이터를 기반으로, **가장 인기 있어 보이는 맛집 3곳과 놀거리 3곳을 뽑고 추천 코스**를 제시하는 AI입니다.

입력:
- 맛집 리스트 (총 {len(restaurants)}개):
{format_places(restaurants)}

- 놀거리 리스트 (총 {len(hot_places)}개):
{format_places(hot_places)}

지침:
1. 이름과 주소를 기반으로 직관적으로 인기 있어 보이는 곳을 각각 3곳씩 선택하세요.
2. 판단 기준은 당신의 일반적인 상식과 거리 감각, 이름의 유명도 등을 활용하세요.
3. 공연장을 출발지로, 아래 예시처럼 **총 3개의 추천 코스**를 작성하세요.

응답 형식 (다른 말 절대 하지 마세요):

추천 맛집 TOP3:
1. [이름]
2. [이름]
3. [이름]

추천 놀거리 TOP3:
1. [이름]
2. [이름]
3. [이름]

추천 코스:
1. 공연장 → [맛집1] → [놀거리1]
2. 공연장 → [맛집2] → [놀거리2]
3. 공연장 → [맛집3] → [놀거리3]
"""

#추천 맛집, 추천 놀거리 list로 뽑기
def extract_block(text: str, title: str) -> list[str]:
    pattern = rf"{title}\s*TOP3:\s*\r?\n((?:\d+\..+(?:\r?\n|$))+)"    
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return []
    lines = match.group(1).strip().splitlines()
    return [re.sub(r"^\d+\.\s*", "", line).strip() for line in lines]

#추천 코스 뽑기
def extract_courses(text: str) -> list[str]:
    pattern = r"추천\s*코스:\s*\r?\n((?:\d+\..+(?:\r?\n|$))+)"
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return []
    lines = match.group(1).strip().splitlines()
    return [re.sub(r"^\d+\.\s*", "", line).strip() for line in lines]

#뽑은 장소 request와 매칭되면 request 정보 전체 return
def find_matching_places(selected_names: list[str], full_list: List[KakaoResponse]) -> List[KakaoResponse]:
    result: List[KakaoResponse] = []
    for raw_name in selected_names:
        name = re.sub(r"\s+", "", raw_name).strip().lower()
        for raw_place in full_list:
            place = re.sub(r"\s+", "", raw_place.place_name).strip().lower()

            if place == name and raw_place not in result:
                result.append(raw_place)
                break
    return result

def to_activity_dto(p: KakaoResponse, typ: str) -> dict:
    dto = ActivityDTO(
        activity_name=p.place_name,
        address_name=p.address_name,
        latitude=float(p.y),
        longitude=float(p.x),
        activity_type=typ
    )
    return dto.model_dump()

def recommend_activity(restaurants: List[KakaoResponse], hot_places: List[KakaoResponse]) -> dict:
    prompt = build_prompt(restaurants, hot_places)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512
    }
    try:
        response = requests.post(invoke_url, headers=headers, data=json.dumps(body))
        print(response)
        print("Raw Response Text:\n", response.text)

        content_list = response.json().get("content", [])
        if isinstance(content_list, list) and len(content_list) > 0:
            aiResult = content_list[0].get("text", "")
        else:
            aiResult = ""
    except Exception as e:
            raise RuntimeError(f"AI 호출 실패: {e}")
    
    restaurant_names = extract_block(aiResult, "추천 맛집")
    hot_place_names = extract_block(aiResult, "추천 놀거리")
    courses = extract_courses(aiResult)

    result_restaurants = find_matching_places(restaurant_names, restaurants)
    result_hot_places  = find_matching_places(hot_place_names, hot_places)
    
    return {
        "restaurants": [to_activity_dto(p, "Restaurant") for p in result_restaurants],
        "hot_places":  [to_activity_dto(p, "HotPlace") for p in result_hot_places],
        "course1": courses[0] if len(courses) > 0 else "",
        "course2": courses[1] if len(courses) > 1 else "",
        "course3": courses[2] if len(courses) > 2 else ""
    }

