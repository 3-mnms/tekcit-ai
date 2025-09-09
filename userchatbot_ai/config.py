# userchatbot_ai/chatbot_config.py
import os
from dotenv import load_dotenv

load_dotenv()

# .env 파일에서 Bedrock 관련 환경 변수를 가져오기
region = os.getenv("AWS_BEDROCK_REGION")
api_key = os.getenv("AWS_BEDROCK_API_KEY")
claude_model_id = "anthropic.claude-3-haiku-20240307-v1:0"
titan_model_id = "amazon.titan-embed-text-v2:0"

# Bedrock Runtime 엔드포인트 URL을 직접 구성
base_url = f"https://bedrock-runtime.{region}.amazonaws.com"
invoke_url = f"{base_url}/model/{claude_model_id}/invoke"

titan_config = {
    "model_id": titan_model_id,
    "region_name": region
}

# 요청에 사용할 헤더를 구성
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}