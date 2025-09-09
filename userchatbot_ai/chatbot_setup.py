# userchatbot_ai/chatbot_setup.py
import os
import sys
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_chroma import Chroma

# .env 파일 로드
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_path)
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)

sys.path.append(project_root)

# 1. 문서 로드 
# 스크립트 파일의 현재 위치를 기준으로 파일 경로를 정확하게 지정
script_directory = os.path.dirname(os.path.abspath(__file__))
document_path = os.path.join(script_directory, "테킷_이용정책.txt")
loader = TextLoader(document_path, encoding="utf-8")
documents = loader.load()

# 2. 텍스트 분할
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n제", "\n\n", "\n", " "]
)
split_docs = text_splitter.split_documents(documents)
print(f"총 {len(split_docs)}개의 문서 조각으로 분할되었습니다.")

# 3. Bedrock 임베딩 모델 초기화
embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")

# 4. ChromaDB에 저장
# DB 저장 경로도 절대 경로로 지정하여 안정성을 높이기
db_directory = os.path.join(script_directory, "chroma_db")
vectorstore = Chroma.from_documents(
    documents=split_docs,
    embedding=embeddings,
    persist_directory=db_directory
)

print(f"문서 벡터 DB 생성 완료! '{db_directory}' 폴더가 생성되었습니다.")