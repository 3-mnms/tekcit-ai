import os
import json
import requests
from userchatbot_ai.config import invoke_url, headers, titan_config
from langchain_aws import BedrockEmbeddings
from langchain_chroma import Chroma
# # --- 1. 경로 및 환경 설정 ---
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
너는 '테킷(Tekcit)'의 전문 고객센터 직원이야. 항상 친절하고 명확한 말투로 답변해야 해.

아래에 제공된 '자료'만을 바탕으로 사용자의 '질문'에 대해 답변해 줘.
- 정책을 그대로 인용하거나 보여주지 말고, 핵심 내용을 자연스럽게 풀어서 설명해야 해.
- 답변은 두세 문장 이내로 간결하게 핵심만 전달해야 해.
- 자료에 없는 내용은 절대 지어내지 말고,
  "죄송하지만 문의하신 내용은 정책에서 찾을 수 없습니다." 라고 답변해야 해.

--- 자료 ---
{context}

--- 질문 ---
{question}
"""

# --- 4. Claude 3 Haiku 호출 ---
def ask_chatbot(question: str) -> str:
    # 이전 대화 관련 키워드 차단
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

    # 3. (Generation) Claude 3 Haiku 호출
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024
    }

    try:
        response = requests.post(invoke_url, headers=headers, data=json.dumps(body))
        response.raise_for_status()

        response_json = response.json()
        content_list = response_json.get("content", [])

        if content_list and isinstance(content_list, list):
            raw_answer = content_list[0].get("text", "답변을 생성하지 못했습니다.")
            
            #후처리: 인사말 + 본문 + 마무리
            final_answer = f"안녕하세요 고객님! 테킷 고객센터 챗봇입니다.\n\n{raw_answer.strip()} 감사합니다."
            return final_answer

        return "빈 답변이 수신되었습니다."

    except requests.exceptions.HTTPError as http_err:
        return f"챗봇 호출 실패 (HTTP 오류): {http_err}\n응답 내용: {response.text}"
    except Exception as e:
        return f"챗봇 호출 중 오류 발생: {e}"

# 단독 실행 시 테스트
if __name__ == '__main__':
    question = "공연 5일 전에 취소하면 수수료 얼마인가요?"

    print("--- 질문 ---")
    print(question)

    answer = ask_chatbot(question)

    print("\n--- 답변 ---")
    print(answer)
