import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))

class Config:
    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    EMBED_MODEL = os.getenv("OPENAI_EMBEDDING")
    
    # Embed Type
    EMBED_TYPE = os.getenv("EMBED_TYPE")
    
    # ChromaDB
    CHROMADB_PATH = os.getenv("CHROMADB_PATH")
    
    # Chat History
    CHAT_HISTORY_PATH = os.getenv("CHAT_HISTORY_PATH")
    
    # FastAPI 서버
    API_URL = os.getenv("API_URL")
    
    # PostgreSQL 데이터베이스
    DB_CONFIG = {
        "dbname": os.getenv("DATABASE_NAME")
        , "user": os.getenv("DATABASE_USER")
        , "password": os.getenv("DATAPASE_PASSWORD")
        , "host": os.getenv("DATABASE_HOST")
        , "port": os.getenv("DATAPASE_PORT")
    }
    
    # JWT 토큰
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # 면접 프롬프트 설정
    BASE_QUESTIONS = list(map(int, os.getenv("BASE_QUESTIONS").split(",")))
    MAX_FOLLOWUP_QUESTIONS = int(os.getenv("MAX_FOLLOWUP_QUESTIONS"))
    
    # 면접 질문 수
    QUESTION_NUM = int(os.getenv("QUESTION_NUM"))
