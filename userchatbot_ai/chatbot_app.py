import os
import json
import requests
from userchatbot_ai.config import titan_config
from langchain_aws import BedrockEmbeddings
from langchain_chroma import Chroma
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.session import get_session

# --- 1. 경로 및 환경 설정 ---
current_path = os.path.dirname(os.path.abspath(__file__))

# --- 2. 임베딩 및 ChromaDB 로드 ---
embeddings = BedrockEmbeddings(**titan_config)

persist_directory = os.path.join(current_path, "chroma_db")
vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

# --- 3. 프롬프트 생성 ---
def build_prompt(question, context):
    return f"""
너는 '테킷(Tekcit)'의 전문 고객센터 직원 "티키"다.  
역할극처럼 대답하지 말고, 고객 문의에 답변하는 실제 상담원처럼 행동해야 한다.  

[인사말 규칙]  
- 답변 맨 앞에만 "안녕하세요, 테킷 고객센터 챗봇 티키입니다." 라는 고정된 인사말을 사용한다.  
- 인사말은 딱 한 번만 한다.  
- 답변의 본문과 마지막에는 절대 인사말이나 자기소개를 반복하지 않는다.  

[답변 규칙]  
- 아래 제공된 '자료'만을 바탕으로 사용자의 질문에 답변한다.  
- 정책을 그대로 인용하지 말고, 핵심 내용을 두세 문장 이내로 간결하게 풀어쓴다.  
- 항상 존댓말을 사용하고, 공손하고 명확하게 말한다.  
- 자료에 없는 내용은 절대 지어내지 말고,  
  "죄송하지만 문의하신 내용은 정책에서 찾을 수 없습니다." 라고 답변한다.  

--- 자료 ---
{context}

--- 질문 ---
{question}
"""

# --- 4. SigV4 요청 유틸 ---
def signed_request(payload: dict):
    region = os.getenv("AWS_REGION", "ap-northeast-2")
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    endpoint = f"https://bedrock-runtime.{region}.amazonaws.com/model/{model_id}/invoke"

    session = get_session()
    creds = session.get_credentials().get_frozen_credentials()

    # SigV4 서명 추가
    request = AWSRequest(method="POST", url=endpoint, data=json.dumps(payload))
    SigV4Auth(creds, "bedrock", region).add_auth(request)

    return requests.post(
        endpoint,
        headers=dict(request.headers),
        data=request.body
    )

# --- 5. Claude 3 Haiku 호출 ---
def ask_chatbot(question: str) -> str:
    # 0. 이전 대화 관련 키워드 차단
    memory_keywords = ["저번에", "방금", "방금 전", "아까", "직전"]
    if any(keyword in question for keyword in memory_keywords):
        return (
            "죄송합니다만, 고객센터 챗봇은 이전 대화 내용을 기억하거나 저장하지 않습니다. "
            "문의하실 내용을 다시 말씀해 주시면 정책 자료를 기반으로 답변해 드릴게요."
        )

    # 1. (Retrieval) 관련 문서 검색
    retriever = vectorstore.as_retriever()
    retrieved_docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    # 2. (Augmentation) 프롬프트 생성
    prompt = build_prompt(question, context)

    # 3. (Generation) Bedrock 호출
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024
    }

    try:
        response = signed_request(body)
        response.raise_for_status()

        response_json = response.json()
        content_list = response_json.get("content") or []

        if content_list and isinstance(content_list, list):
            raw_answer = content_list[0].get("text", "답변을 생성하지 못했습니다.")
            final_answer = raw_answer.strip()
            return final_answer

        return "빈 답변이 수신되었습니다."

    except requests.exceptions.HTTPError as http_err:
        return f"챗봇 호출 실패 (HTTP 오류): {http_err}\n응답 내용: {response.text}"
    except Exception as e:
        return f"챗봇 호출 중 오류 발생: {e}"

# 단독 실행 시 테스트
if __name__ == '__main__':
    q = "공연 5일 전에 취소하면 수수료 얼마인가요?"
    print("--- 질문 ---")
    print(q)
    print("\n--- 답변 ---")
    print(ask_chatbot(q))