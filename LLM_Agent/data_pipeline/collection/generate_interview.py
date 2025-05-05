import os
import sys
import json
from tqdm import tqdm
from typing import List, Dict

from langchain_core.prompts import ChatPromptTemplate

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.externals import set_llm

positions = [
    {"tag_eng": "Data Engineer", "tag_kor": "데이터 엔지니어"},
    {"tag_eng": "Machine Learning Engineer", "tag_kor": "머신러닝 엔지니어"},
    {"tag_eng": "Data Analyst", "tag_kor": "데이터 분석가"},
    {"tag_eng": "AI Engineer", "tag_kor": "AI 엔지니어"},
    {"tag_eng": "AI Researcher", "tag_kor": "AI 연구원"}
]
experiences = ["신입", "1-3년", "3-5년", "5-10년", "10년이상"]
    
prompt = ChatPromptTemplate.from_template(
    """
    당신은 채용 담당 실무 면접관입니다.

    "{position}" 포지션의 "{experience}" 채용을 위한 면접 질문 25가지와 각 질문에 대한 모범 답변을 제시해주세요.
    실제 면접 상황을 가정해서 질문과 답변의 형식으로 제시해주세요.
    질문의 내용은 직무에 대한 이해와 기술적인 요소를 적절하게 섞어서 출제해주세요.
    질문과 답변은 모두 구체적으로 제시해주세요.
    
    각 질문에 대해서 질문의 핵심 키워드를 직무 이해도, 기술 활용 능력, 문제 해결 능력 중 한 가지를 함께 제시해주세요.

    응답 형식은
    질문:
    키워드:
    답변:

    으로 다른 표현은 불필요합니다. 번호도 붙이지 마세요.
    """
)

llm = set_llm(0.7)
chain = prompt | llm

output_json = "storage/raw_data/QA/interview.json"

def generate_qa_from_gpt(position: str, experience: str, tag_eng: str, tag_kor: str) -> List[Dict]:
    result = chain.invoke({
            "position": position,
            "experience": experience
        })
    print(result.content)

    qa_list = []
    question = None
    
    for line in result.content.strip().split("\n"):
        if line.startswith("질문:"):
            question = line.replace("질문: ", "").strip()
        elif line.startswith("키워드:") and question:
            keyword = line.replace("키워드: ", "").strip()
        elif line.startswith("답변:") and question:
            answer = line.replace("답변: ", "").strip()
            
            qa_list.append({
                "tag_eng": tag_eng,
                "tag_kor": tag_kor,
                "experience": experience,
                "question": question,
                "keyword": keyword,
                "answer": answer
            })
            question = None

    return qa_list

def generate_and_save():
    qa_results = []
    
    for position in tqdm(positions, desc="Generating Q&A by GPT"):
        for exp in experiences:
            qas = generate_qa_from_gpt(position["tag_kor"], exp, position["tag_eng"], position["tag_kor"])
            qa_results.extend(qas)
            print(len(qa_results))

            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(qa_results, f, ensure_ascii=False, indent=4)
                
    print(f"> 저장 완료: {output_json}")

if __name__ == "__main__":
    generate_and_save()