import json
import requests
from review_ai.config import invoke_url, headers

def buildPrompt(summary, new_review, p_count, neg_count, neu_count):
    return f"""
당신은 공연 기대평을 요약하고 감정을 분석하는 AI입니다.
입력:
- 집단 요약: "{summary}"
- 새 리뷰(1표): "{new_review}"
- 집계: 긍정={p_count}, 부정={neg_count}, 중립={neu_count}
지침:
1.집단 요약을 기본 톤으로 유지하고, 새 리뷰가 다르면 "대체로 ~, 한편/일부는 ~라는 의견도 있었다."로 한 문장 균형 요약.
("기존에는~/새로운 평은~" 금지, 단정 금지)
2.새 기대평의 감정을 '긍정', '부정', '중립' 중 하나로 판단해주세요.

응답은 반드시 아래 형식으로 해주세요 (다른 말 절대 하지 마세요):
-감정: 긍정
-요약: (요약문)
"""
    
def extractResult(result, key):
    for line in result.split("\n"):
        if line.strip().startswith(f"-{key}:"):
            return line.split(":", 2)[1].strip()
    return ""
          
def review_analyze(summary, new_review, p_count, neg_count, neu_count):
    prompt = buildPrompt(summary, new_review, p_count, neg_count, neu_count)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512
    }
    try:
        response = requests.post(invoke_url, headers=headers, data=json.dumps(body))
        print("🔎 Raw Response Text:\n", response.text)

        content_list = response.json().get("content", [])
        if isinstance(content_list, list) and len(content_list) > 0:
            aiResult = content_list[0].get("text", "")
        else:
            aiResult = ""
    except Exception as e:
            raise RuntimeError(f"AI 호출 실패: {e}")
    
    emotion = extractResult(aiResult, "감정");
    new_summary = extractResult(aiResult, "요약");

    if emotion == "긍정":
        p_count+=1
                
    elif emotion == "부정":
        neg_count+=1
            
    elif emotion == "중립":
        neu_count+=1

    return {
        "summary": new_summary,
        "emotion": emotion,
        "positive_count": p_count,
        "negative_count": neg_count,
        "neutral_count": neu_count,
    }

