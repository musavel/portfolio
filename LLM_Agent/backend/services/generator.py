import os
import sys
import re
import random
from typing import Dict, Optional
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, FewShotPromptTemplate
from langchain_core.output_parsers import StrOutputParser

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.core.chroma import ChromaSearch
from models.externals import set_llm

class Generator:
    def __init__(self, use_llm=True, temperature=0.5):
        if use_llm:
            self.llm = set_llm(temperature)
        else:
            self.llm = None

    def generate_description(self, position: str, experience: str) -> str:
        document = ChromaSearch("job_description")
        
        prompt = ChatPromptTemplate.from_template(
            """
                너는 채용 담당자를 도와 직무 기술서를 생성하는 AI야.

                다음은 "{position}" 포지션에 대해 다양한 경력 수준에서 추출된 기존 JD 항목들이야.  
                너의 임무는 "{experience}" 경력자에게 적합한 직무 기술서를 새로 작성하는 것이야.

                아래 내용을 참고하되:
                - 경력 범위가 다를 수 있으니, "{experience}" 수준에 맞는 내용만 골라줘
                - 중복되거나 불필요한 항목은 제거하고
                - 자연스럽고 현실적인 직무 기술서를 작성해줘

                반드시 아래 세 가지 섹션으로 구분하고 한 줄씩 띄워서 마크다운 형식이 아닌 일반 문서처럼 작성해:
                [주요 업무]
                - 
                -
                
                [자격 요건]
                -
                -
                
                [우대 사항]
                -
                -

                [참고: 주요 업무]
                {tasks}

                [참고: 자격 요건]
                {requires}

                [참고: 우대 사항]
                {preferences}

                자체적인 서비스나 회사 이름에 대한 언급이 있다면 반드시 제외해줘.
            """
        )

        tasks = document.get_description(position, experience, "tasks")
        requires = document.get_description(position, experience, "requires")
        preferences = document.get_description(position, experience, "preferences")

        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "position": position,
            "experience": experience,
            "tasks": tasks,
            "requires": requires,
            "preferences": preferences
        })
        
    def generate_question(self, position: str, experience: str, num: int) -> str:
        document = ChromaSearch("interview")
        
        prompt = ChatPromptTemplate.from_template(
            """
                당신은 특정 직무(position)와 경력 수준(experience)에 맞는 면접 질문을 생성하는 AI입니다.

                다음은 참고할 수 있는 기출 면접 질문 문서입니다:
                [기출 면접 질문 문서: {question}]
                > 문서의 각 행은 (키워드): 면접 질문 형태로 되어 있습니다

                사용자로부터 아래 정보를 입력받았습니다:
                - 직무(Position): {position}
                - 경력 수준(Experience): {experience}

                위 정보를 바탕으로 아래 조건을 만족하는 면접 질문 리스트를 생성해주세요:

                1. 사용자의 직무와 경력 수준에 가장 적합한 질문을 선택하거나, 문서를 바탕으로 유사한 질문을 생성합니다.
                2. 문서에 중복이 있다면 중요한 질문임을 가정하고 반드시 출제해 주세요.
                3. 총 {nums}개의 면접 질문을 제시해주세요.
                4. 질문은 가급적 실제 면접에서 활용 가능한 형태로 자연스럽게 작성해주세요.
                5. 질문의 키워드를 아래 형식에 반영해주세요.
                6. 각 키워드를 골고루 순서대로 분배해서 출제해주세요.
                7. 존댓말을 사용해주세요.

                [면접 질문]
                
                1. [키워드]
                > (질문)
                
                2. [키워드]
                > (질문)
            """
        )

        question = document.get_question(position, experience)

        chain = prompt | self.llm | StrOutputParser()
        
        return chain.invoke({
            "position": position,
            "experience": experience,
            "question": question,
            "nums": num
        })
        
    def generate_interview(self, position: str, experience: str, nums: Dict[str, int]) -> str:
        document = ChromaSearch("interview")
        result = {}
        
        for keyword, num in nums.items():
            interview_data = document.get_interview(position, experience, keyword)
            
            if not interview_data or keyword not in interview_data:
                result[keyword] = []
                continue
            
            qa_pairs = interview_data[keyword]
            random.shuffle(qa_pairs)
            
            # 불러온 질문의 갯수가 num보다 적으면 전체를 반환
            selected_pairs = qa_pairs[:min(len(qa_pairs), num)]
            
            result[keyword] = selected_pairs

        return result

    def generate_followup(self, position: str, experience: str, previous_question: str, user_answer: str) -> Optional[str]:
        
        prompt = ChatPromptTemplate.from_template(
            """
                당신은 {position} 포지션에 지원한 {experience} 경력 지원자를 면접 중인 면접관입니다.

                다음은 이전에 제시한 질문과 이에 대한 지원자의 답변입니다.

                - 이전 질문: {previous_question}
                - 지원자 답변: {user_answer}

                지원자의 답변을 바탕으로 후속 질문(꼬리 질문)을 한 가지 생성해주세요.
                
                아래 기준에 따라 후속 질문의 난이도와 방향을 조절해 주세요:
                
                - 질문에 대해 모르겠다고 답변을 한 경우
                → 유사하지만 조금 더 쉬운 질문으로 변경해주세요.

                - 답변이 구체적이지 않거나 핵심이 부족한 경우  
                → 질문을 조금 더 쉬운 표현으로 바꾸거나, 더 구체적인 상황/방법을 요청해 주세요.

                - 답변에 중요한 키워드, 개념, 도구, 경험 등이 언급된 경우  
                → 해당 내용을 더 깊이 있게 탐색할 수 있는 질문으로 발전시켜 주세요.

                - 답변이 모호하거나 방향이 맞지 않는 경우  
                → 본래 질문의 핵심을 다시 짚는 방식으로 다시 물어봐 주세요.

                - 답변이 충분히 구체적이고 완성도 높은 경우  
                → 그 내용을 기반으로 더 고차원적인 문제 해결 능력이나 응용 능력을 평가할 수 있는 질문으로 발전시켜 주세요.

                **사용자의 답변을 짧고 간결하게 언급해주시고, 질문만 반환해 주세요. 불필요한 설명은 생략하고, 실제 면접 상황처럼 자연스럽고 존댓말로 작성해 주세요.
            """
        )
        
        chain = prompt | self.llm | StrOutputParser()

        return chain.invoke({
            "position": position,
            "experience": experience,
            "previous_question": previous_question,
            "user_answer": user_answer
        })
        
    def generate_feedback(self, position: str, experience: str, interview_history: Dict) -> str:
        prompt = ChatPromptTemplate.from_template(
            """
                당신은 유능한 실무 면접관 입니다.
                다음은 '{position}' 포지션 ({experience} 경력)의 지원자가 인터뷰에서 남긴 답변들입니다.
                아래 지원자의 전체 답변을 종합적으로 평가해 주세요.

                전체 질문:
                {questions}
                지원자 답변
                {answers}

                [평가 기준]
                1. 직무 이해도
                2. 기술 활용 능력
                3. 문제 해결 능력
                4. 전체 평가

                각 항목에 대해 전문적인 평가 피드백을 제시해주세요.
                점수는 필요하지 않습니다.
                큰 제목도 필요하지 않습니다. 평가 기준에 대해서만 제목을 달아주세요.
            """
        )

        questions = "\n".join([q for q in interview_history["question"]])
        answers = "\n".join([q for q in interview_history["user_answer"]])

        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke(
            {
                "position": position,
                "experience": experience,
                "questions": questions,
                "answers": answers
            }
        )

        return response

    def generate_answer(self, position: str, experience: str, interview_history: Dict) -> str:
        document = ChromaSearch("interview")
        results = []

        for question, answer, example_answer in zip(
            interview_history["question"], 
            interview_history["user_answer"], 
            interview_history["example_answer"]
        ):
            # 기존 질문인 경우 (example_answer가 None이 아닌 경우)
            if example_answer is not None:
                # 벡터 DB에서 유사한 답변 검색
                similar_answer = document.get_answer(position, experience, question)
                
                if similar_answer:
                    # 유사한 답변이 있으면 그대로 사용
                    results.append(f"(질문): {question}\n(답변): {similar_answer}")
                    continue

            # 새로 생성된 질문이거나 유사한 답변을 찾지 못한 경우 few-shot으로 생성
            examples = []
            for q, a, e in zip(interview_history["question"], interview_history["user_answer"], interview_history["example_answer"]):
                if e is not None:
                    examples.append(
                        {
                            "question": q,
                            "user_answer": a,
                            "example_answer": e
                        }
                    )

            example_prompt = PromptTemplate(
                input_variables=["question", "user_answer", "example_answer"],
                template="""
                    질문: {question}
                    지원자 답변: {user_answer}
                    모범 답변: {example_answer}
                    """.strip()
            )

            few_shot_prompt = FewShotPromptTemplate(
                examples=examples,
                example_prompt=example_prompt,
                prefix=f"""
                    당신은 유능한 실무 면접관 입니다.
                    다음은 '{position}' 포지션 ({experience} 경력)의 지원자가 인터뷰에서 남긴 답변과 그에 대한 모범답변 예시입니다.
                    이 예시들을 참고하여 질문에 대해 이상적인 모범 답변을 작성해 주세요.
                    일부 질문은 위 예시에서 모범 답변이 제공되지 않았을 수도 있지만, 그런 경우에도 스스로 적절한 답변을 생성해 주세요.
                    질문 내용은 바꾸지 말고, 모범 답변은 반드시 존댓말로 작성해 주세요.
                """,
                suffix="""
                    전체 질문:
                    {question}
                    지원자 답변
                    {answer}

                    [모범 답변]
                    (질문): ...
                    (답변): ...
                    """,
                input_variables=["question", "answer"]
            )

            chain = few_shot_prompt | self.llm | StrOutputParser()
            response = chain.invoke(
                {
                    "position": position,
                    "experience": experience,
                    "question": question,
                    "answer": answer
                }
            )
            results.append(response)

        return "\n\n".join(results)