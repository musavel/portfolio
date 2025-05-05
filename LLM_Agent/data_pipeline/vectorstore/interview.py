import os
import sys
import re
import json
from tqdm import tqdm
from langchain_core.documents import Document

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import Config
from models.externals import set_embedding
from models.vector import set_vectorstore
from data_pipeline.utils.experience_range import parse_experience_range

save_path = Config.CHROMADB_PATH
input_json = os.path.join("storage", "raw_data", "QA", "interview.json")
collection_name = "interview"

embedding = set_embedding(Config.EMBED_TYPE)
vectorstore = set_vectorstore(collection_name, embedding)
    
def load_and_store():
    with open(input_json, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    docs = []
    tag_counters = {}

    for row in tqdm(raw_data, desc="문서 생성 중"):
        tag = row["tag_eng"]
        
        if tag not in tag_counters:
            tag_counters[tag] = 1
        
        words = tag.split()
        if len(words) >= 2:
            qa_id = f"{words[0][0]}{words[1][0]}{tag_counters[tag]}"
            tag_counters[tag] += 1
        else:
            qa_id = f"{row['tag_eng'][:2]}{len(docs) + 1}"
            
        base_meta = {
            "collection_name": collection_name
            , "qa_id": qa_id
            , "tag_eng": row["tag_eng"]
            , "tag_kor": row["tag_kor"]
            , "experience": row["experience"]
            , "keyword": row["keyword"]
            , "answer": row["answer"]
        }

        if not row.get("question"):
            continue

        doc_text = row["question"]

        # LangChain Document 구성
        doc = Document(
            page_content=doc_text,
            metadata={
                **base_meta
            }
        )
        docs.append(doc)
            
    print(f"> {len(docs)}개의 문서를 임베딩 후 ChromaDB에 저장합니다.")
    vectorstore.add_documents(docs)
    print(f"> 저장 완료! 위치: {save_path}")
    
if __name__ == "__main__":
    load_and_store()