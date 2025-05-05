import os
import sys
import re
import json
from tqdm import tqdm
from langchain_core.documents import Document

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import Config
from models.externals import set_embedding
from models.vector import set_vectorstore
from data_pipeline.utils.experience_range import parse_experience_range

save_path = Config.CHROMADB_PATH
input_json = os.path.join("storage", "raw_data", "JD", "job_details.json")
collection_name = "job_description"

embedding = set_embedding(Config.EMBED_TYPE)
vectorstore = set_vectorstore(collection_name, embedding)

def load_and_store():
    with open(input_json, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    docs = []

    for row in tqdm(raw_data, desc="문서 생성 중"):
        base_meta = {
            "collection_name": collection_name
            , "page_id": str(row["page_id"])
            , "tag_eng": row["tag_eng"]
            , "tag_kor": row["tag_kor"]
        }

        for field in ["tasks", "requires", "preferences"]:
            if not row.get(field):
                continue

            doc_text = row[field]
            doc_type = field

            # LangChain Document 구성
            min_exp, max_exp = parse_experience_range(row["experience"])
            doc = Document(
                page_content=doc_text,
                metadata={
                    **base_meta,
                    "min_exp": str(min_exp),
                    "max_exp": str(max_exp),
                    "doc_type": doc_type
                }
            )
            docs.append(doc)
            
    print(f"> {len(docs)}개의 문서를 임베딩 후 ChromaDB에 저장합니다.")
    vectorstore.add_documents(docs)
    print(f"> 저장 완료! 위치: {save_path}")
    
if __name__ == "__main__":
    load_and_store()