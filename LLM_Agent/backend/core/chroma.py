import os
import sys
import re
from typing import List, Optional
from collections import defaultdict
from langchain.schema import Document
from langchain_chroma.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

from models.externals import set_embedding
from models.vector import set_vectorstore
from data_pipeline.utils.experience_range import parse_experience_range

class ChromaSearch:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.embedding = set_embedding(Config.EMBED_TYPE)
        self.vectorstore = set_vectorstore(collection_name, self.embedding)

    def _overlap(self, a_min, a_max, b_min, b_max) -> bool:
        return max(a_min, b_min) <= min(a_max, b_max)
    
    def _filter_by_experience(self, docs, min_exp, max_exp) -> List:
        filtered = []
        
        for doc in docs:
            try:
                doc_min_exp = int(doc.metadata.get("min_exp", 0))
                doc_max_exp = int(doc.metadata.get("max_exp", 50))
                if self._overlap(min_exp, max_exp, doc_min_exp, doc_max_exp):
                    filtered.append(doc)
            except Exception as e:
                print(f"필터링 오류: {e}")
                
        return filtered

    def get_description(self, position: str, experience: str, doc_type: str, k=15) -> List[Document]:
        exp_min, exp_max = parse_experience_range(experience)
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": k,
                "filter": {
                    "$and": [
                        {"collection_name": {"$eq": self.collection_name}}
                        , {"tag_kor": {"$eq": position}}
                        , {"doc_type": {"$eq": doc_type}}
                    ]
                }
            }
        )
        
        query = f"{position} {doc_type}"
        docs = retriever.invoke(query)
        
        filtered = self._filter_by_experience(docs, exp_min, exp_max)

        print(f"\n[{doc_type.upper()}] 필터링된 문서: {[doc.metadata.get('page_id') for doc in filtered]}")

        return "\n".join([doc.page_content for doc in filtered])
    
    def get_question(self, position: str, experience: str, k=30) -> List[Document]:
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": k,
                "filter": {
                    "$and": [
                        {"collection_name": {"$eq": self.collection_name}}
                        , {"tag_kor": {"$eq": position}}
                        , {"experience": {"$eq": experience}}
                    ]
                }
            }
        )
        
        query = f"{position}"
        docs = retriever.invoke(query)

        print(f"\n필터링된 문서 수: {len(docs)}")

        return "\n".join([f"{doc.metadata.get('keyword')}: {doc.page_content}" for doc in docs])
    
    def get_interview(self, position: str, experience: str, keyword: str, k=20) -> List[dict]:
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": k,
                "filter": {
                    "$and": [
                        {"collection_name": {"$eq": self.collection_name}}
                        , {"tag_kor": {"$eq": position}}
                        , {"keyword": {"$eq": keyword}}
                        , {"experience": {"$eq": experience}}
                    ]
                }
            }
        )
        
        data_list = defaultdict(list)
        
        query = f"{position}"
        docs = retriever.invoke(query)
        
        print(f"\n[{keyword}] 필터링된 문서 수: {len(docs)}")
        
        for doc in docs:
            question = doc.page_content
            answer = doc.metadata.get("answer")
            keyword = keyword
            
            data_list[keyword].append({
                "question": question,
                "answer": answer
            })

        return dict(data_list)

    def get_answer(self, position: str, experience: str, question: str, k=3) -> Optional[str]:
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": k,
                "filter": {
                    "$and": [
                        {"collection_name": {"$eq": self.collection_name}},
                        {"tag_kor": {"$eq": position}},
                        {"experience": {"$eq": experience}}
                    ]
                }
            }
        )
        
        # 질문으로 유사도 검색 수행
        docs = retriever.invoke(question)
        
        if not docs:
            return None
            
        # 가장 유사한 질문의 답변 반환
        most_similar_doc = docs[0]
        return most_similar_doc.metadata.get("answer")