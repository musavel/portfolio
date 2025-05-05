import os
import sys
import pandas as pd
from tqdm import tqdm

from langchain_core.prompts import ChatPromptTemplate

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.externals import set_llm

role_dict = {
    "Data Analyst": "데이터 분석가"
    , "Data Engineer": "데이터 엔지니어"
    , "Data Scientist": "데이터 사이언티스트"
    , "Machine Learning Engineer": "머신러닝 엔지니어"
    , "Deep Learning Engineer": "딥러닝 엔지니어"
    , "MLOps Engineer": "MLOps 엔지니어"
    , "AI Engineer": "AI 엔지니어"
    , "AI Researcher": "AI 연구원"
}

prompt = ChatPromptTemplate.from_template(
    """
    다음 직무명을 아래 리스트 중 하나로 분류해주세요. 해당되지 않으면 '기타'로 답해주세요.
    최대한 아래 리스트 중에서 골라줬으면 좋겠습니다.
    다음 직무명의 키워드가 리스트 중에서 두 개의 직무와 겹친다면, 우선 순위를 자동으로 설정해서 답해주세요.

    직무 리스트:
    {roles}

    직무명: "{position_name}"

    반드시 위 리스트에 있는 단어 또는 '기타' 중 하나만 출력하세요.
    """
)

llm = set_llm(0)
chain = prompt | llm

raw_data_path = os.path.join("storage", "raw_data", "JD")
input_csv = os.path.join(raw_data_path, "summary_raw.csv")
output_csv = os.path.join(raw_data_path, "summary.csv")

def tag_with_llm(position_name: str) -> str:
    try:
        result = chain.invoke({
            "position_name": position_name,
            "roles": ", ".join(role_dict.keys())
        })
        return result.content.strip()
    
    except Exception as e:
        return "기타"

def tag_and_save():
    df = pd.read_csv(input_csv, encoding="utf-8-sig")

    tqdm.pandas(desc="> LangChain 태깅 중")
    df["tag_eng"] = df["position_name"].progress_apply(tag_with_llm)
    df["tag_kor"] = df["tag_eng"].map(role_dict).fillna("기타")

    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"> 태깅 완료! 저장 위치: {output_csv}")

if __name__ == "__main__":
    tag_and_save()