import os
from dotenv import load_dotenv
# 환경 변수 로드
load_dotenv()

region = os.getenv("AWS_BEDROCK_REGION")
api_key = os.getenv("AWS_BEDROCK_API_KEY")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

base_url = f"https://bedrock-runtime.{region}.amazonaws.com"
invoke_url = f"{base_url}/model/{model_id}/invoke"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}