import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import os
import sys

# 프로젝트 루트 경로를 Python Path에 추가합니다.
# 이렇게 하면 userchatbot_ai.chatbot_app 모듈을 올바르게 임포트할 수 있습니다.
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)
sys.path.append(project_root)

# chatbot_app.py에서 핵심 함수를 임포트합니다.
from userchatbot_ai.chatbot_app import ask_chatbot

# FastAPI 애플리케이션 인스턴스를 생성합니다.
app = FastAPI()

# --- 1. 요청 및 응답 데이터 모델 정의 ---
# Pydantic을 사용하여 API로 들어오는 데이터의 형식을 정의합니다.
# 이렇게 하면 FastAPI가 자동으로 유효성 검사를 수행합니다.
class ChatRequest(BaseModel):
    """사용자 질문을 담는 요청 모델입니다."""
    question: str

class ChatResponse(BaseModel):
    """챗봇의 답변을 담는 응답 모델입니다."""
    answer: str

# --- 2. API 엔드포인트(Controller) 정의 ---
@app.post("/chat", response_model=ChatResponse)
async def chat_with_tekcit(request: ChatRequest):
    """
    사용자의 질문을 받아 챗봇 답변을 반환하는 API 엔드포인트입니다.
    """
    # 챗봇 코어 함수를 호출하여 답변을 생성합니다.
    # ask_chatbot 함수는 동기 함수이므로 await를 사용하지 않습니다.
    answer = ask_chatbot(request.question)
    
    # 생성된 답변을 Pydantic 모델에 맞춰 반환합니다.
    return ChatResponse(answer=answer)

# --- 3. 개발용 서버 실행 (선택 사항) ---
if __name__ == "__main__":
    # 이 파일을 직접 실행하면 Uvicorn 서버가 시작됩니다.
    uvicorn.run(app, host="0.0.0.0", port=8000)
