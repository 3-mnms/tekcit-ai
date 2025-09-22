from fastapi import APIRouter
from pydantic import BaseModel
from userchatbot_ai.chatbot_app import ask_chatbot
import userchatbot_ai.chatbot_app as chatbot_app
import inspect
from userchatbot_ai import chatbot_app

router = APIRouter()
print("🔥 불러온 ask_chatbot 경로:", inspect.getfile(chatbot_app.ask_chatbot))
print("🔥 chatbot_app 위치:", chatbot_app.__file__)
class ChatRequest(BaseModel):
    """사용자 질문을 담는 요청 모델입니다."""
    question: str

class ChatResponse(BaseModel):
    """챗봇의 답변을 담는 응답 모델입니다."""
    answer: str

@router.post("", response_model=ChatResponse)
async def chat_with_tekcit(request: ChatRequest):
    """
    사용자의 질문을 받아 챗봇 답변을 반환하는 API 엔드포인트입니다.
    """
    # 챗봇 코어 함수를 호출하여 답변을 생성합니다.
    # ask_chatbot 함수는 동기 함수이므로 await를 사용하지 않습니다.
    answer = ask_chatbot(request.question)
    
    # 생성된 답변을 Pydantic 모델에 맞춰 반환합니다.
    return ChatResponse(answer=answer)