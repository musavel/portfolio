import os
import sys
import streamlit as st
import requests
from datetime import datetime
import json
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

API_URL = Config.API_URL

def show():
    st.markdown("""
        ### <span class="custom-heading" style="color: #00cbff !important; font-size: 20px !important;">🤖 가상 면접 챗봇</span>
        AI 면접관과 실시간으로 면접 연습을 진행할 수 있습니다.
        """, unsafe_allow_html=True
    )

    # 상단에 restart 상태 추가
    if "restart" not in st.session_state:
        st.session_state.restart = False
        
    # restart 상태 확인 및 처리
    if st.session_state.restart:
        keys_to_clear = [
            "messages",
            "interview_started",
            "interview_finished",
            "position",
            "experience",
            "base_questions",
            "base_answers",
            "interview_history",
            "question_index",
            "intro_response_shown",
            "current_followup_count",
            "feedback",
            "example_answers",
            "restart"
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # 채팅 기록 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 면접 시작 여부 상태 관리
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
    if "interview_finished" not in st.session_state:
        st.session_state.interview_finished = False
        
    # 질문 관리를 위한 세션 상태 추가
    if "base_questions" not in st.session_state:
        st.session_state.base_questions = []
    if "base_answers" not in st.session_state:
        st.session_state.base_answers = []
    if "interview_history" not in st.session_state:
        st.session_state.interview_history = {"question": [], "user_answer": [], "example_answer": []}
    if "question_index" not in st.session_state:
        st.session_state.question_index = 0

    # 자기소개 응답이 출력되었는지 확인하는 상태 추가
    if "intro_response_shown" not in st.session_state:
        st.session_state.intro_response_shown = False

    # 꼬리 질문 관리를 위한 세션 상태 추가
    if "max_followup_questions" not in st.session_state:
        # 각 질문당 최대 꼬리 질문 횟수
        st.session_state.max_followup_questions = Config.MAX_FOLLOWUP_QUESTIONS
    if "current_followup_count" not in st.session_state:
        st.session_state.current_followup_count = 0

    # 면접이 시작되지 않았을 때만 폼 표시
    if not st.session_state.interview_started:
        with st.form("information_form"):
            position = st.selectbox("포지션", ["포지션 선택", "데이터 분석가", "데이터 엔지니어", "머신러닝 엔지니어", "AI 엔지니어", "AI 연구원"])
            experience = st.selectbox("경력", ["신입", "1-3년", "3-5년", "5-10년", "10년이상"])
            
            submitted = st.form_submit_button("대화 시작", use_container_width=True)
            
            if submitted and position != "포지션 선택":
                with st.spinner("면접 질문을 생성하고 있습니다..."):
                    try:
                        # API 먼저 호출하여 질문 생성
                        response = requests.post(
                            f"{API_URL}/personal/generate/interview",
                            json={
                                "position": position,
                                "experience": experience,
                                "samples": {
                                    '직무 이해도': Config.BASE_QUESTIONS[0]
                                    , '기술 활용 능력': Config.BASE_QUESTIONS[1]
                                    , '문제 해결 능력': Config.BASE_QUESTIONS[2]
                                }
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            for category, category_questions in result.items():
                                for qa in category_questions:
                                    st.session_state.base_questions.append(f"{qa['question']}")
                                    st.session_state.base_answers.append(f"{qa['answer']}")

                            st.session_state.question_index = 0
                            
                            # 면접 시작 상태 설정
                            st.session_state.interview_started = True
                            st.session_state.position = position
                            st.session_state.experience = experience
                            
                            # 초기 면접관 인사 메시지
                            initial_message = f"안녕하세요! {position} 포지션에 지원해 주셔서 감사합니다. 오늘 면접을 진행하게 된 AI 면접관입니다. 먼저 간단하게 자기소개 부탁드립니다."
                            st.session_state.messages.append({"role": "assistant", "content": initial_message})
                            st.rerun()
                            
                        else:
                            st.error("면접 질문 생성 중 오류가 발생했습니다.")
                            
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {str(e)}")

    # CSS 스타일 추가
    st.markdown("""
    <style>
        /* 채팅 컨테이너 스타일 */
        .chat-container {
            padding: 10px;
            max-width: 800px;
            margin: 0 auto;
        }
        
        /* 메시지 공통 스타일 */
        .message {
            padding: 10px 15px;
            border-radius: 15px;
            margin: 8px 0;
            max-width: 45%;
            word-wrap: break-word;
        }
        
        /* 면접관(assistant) 메시지 스타일 */
        .assistant-message {
            background-color: #f0f0f0;
            color: #000000;
            float: left;
            clear: both;
        }
        
        /* 사용자 메시지 스타일 */
        .user-message {
            background-color: #007AFF;
            color: white;
            float: right;
            clear: both;
        }
    </style>
    """, unsafe_allow_html=True)

    # 전체 컨테이너 설정
    chat_container = st.container()
    
    # 입력창을 위한 빈 컨테이너를 먼저 생성
    input_container = st.container()
    
    # 메인 채팅 영역
    if st.session_state.interview_started:  # 면접이 시작된 경우에만 채팅 영역 표시
        with chat_container:
            # 채팅창 컨테이너를 카드 스타일로 만들기
            st.markdown("""
                <style>
                    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
                        background-color: #ffffff;
                        padding: 20px;
                        border-radius: 10px;
                        border: 1px solid #ddd;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                        margin: 10px 0;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # 채팅 영역 헤더
            st.markdown("""
                ### <span class="custom-heading" style="color: #00cbff !important; font-size: 20px !important;">💬 면접 대화</span>
                """, unsafe_allow_html=True
            )
            st.markdown("---")
            
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in st.session_state.messages:
                message_class = "assistant-message" if message["role"] == "assistant" else "user-message"
                st.markdown(
                    f'<div class="message {message_class}">{message["content"]}</div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)
    
    # 입력 영역을 페이지 하단에 배치
    with input_container:
        if st.session_state.interview_started:
            # 메시지에서 면접 종료 여부 확인
            if not st.session_state.interview_finished:
                st.session_state.interview_finished = any("면접이 모두 종료되었습니다" in msg["content"]
                                     for msg in st.session_state.messages if msg["role"] == "assistant")
            
            # 면접이 종료되지 않았을 때만 채팅 입력창 표시
            if not st.session_state.interview_finished:
                if prompt := st.chat_input("답변을 입력하세요"):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    
                    # 자기소개가 완료되었는지 확인
                    is_first_answer = len([m for m in st.session_state.messages if m["role"] == "user"]) == 1
                    
                    if is_first_answer:
                        # 자기소개에 대한 응답 (꼬리 질문 없이 바로 다음 단계로)
                        response_text = "감사합니다. 그럼 지금부터 본격적인 면접을 시작하겠습니다."
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        
                        if st.session_state.base_questions:
                            first_question = st.session_state.base_questions[0]
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": first_question
                            })
                            # 첫 번째 base question 저장
                            st.session_state.interview_history["question"].append(first_question)
                            st.session_state.interview_history["example_answer"].append(st.session_state.base_answers[0])
                            
                            st.session_state.question_index = 1
                            st.session_state.current_followup_count = 0
                    
                    else:
                        with st.spinner("답변해주신 내용을 기반으로 추가 질문을 생성중 입니다..."):
                            try:
                                # 사용자 답변 저장
                                st.session_state.interview_history["user_answer"].append(prompt)
                                
                                # 마지막 질문과 답변 가져오기
                                last_question = st.session_state.interview_history["question"][-1]
                                last_answer = prompt
                                
                                if st.session_state.current_followup_count < st.session_state.max_followup_questions:
                                    response = requests.post(
                                        f"{API_URL}/personal/generate/followup",
                                        json={
                                            "position": st.session_state.position,
                                            "experience": st.session_state.experience,
                                            "previous_question": last_question,
                                            "user_answer": last_answer
                                        }
                                    )
                                    
                                    if response.status_code == 200:
                                        followup_questions = response.json()
                                        followup_text = followup_questions["text"]
                                        
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": followup_text
                                        })
                                        
                                        # 꼬리 질문 저장
                                        st.session_state.interview_history["question"].append(followup_text)
                                        st.session_state.interview_history["example_answer"].append(None)
                                        
                                        st.session_state.current_followup_count += 1
                                    else:
                                        st.error("꼬리 질문 생성 중 오류가 발생했습니다.")
                                        move_to_next_question()
                                else:
                                    move_to_next_question()

                            except Exception as e:
                                st.error(f"오류가 발생했습니다: {str(e)}")
                                move_to_next_question()
                    
                    st.rerun()
            
            # 버튼들을 순차적으로 배치
            if st.session_state.interview_finished:
                # 피드백이 아직 생성되지 않은 경우에만 피드백 생성 버튼 표시
                if "feedback" not in st.session_state:
                    st.markdown("---")
                    if st.button("피드백 생성하기", use_container_width=True):
                        with st.spinner("피드백과 모범 답변을 생성하고 있습니다..."):
                            try:
                                # 피드백 생성 API 호출
                                feedback_response = requests.post(
                                    f"{API_URL}/personal/generate/feedback",
                                    json={
                                        "position": st.session_state.position,
                                        "experience": st.session_state.experience,
                                        "interview_history": st.session_state.interview_history
                                    }
                                )

                                # 모범 답변 생성 API 호출
                                answer_response = requests.post(
                                    f"{API_URL}/personal/generate/answer",
                                    json={
                                        "position": st.session_state.position,
                                        "experience": st.session_state.experience,
                                        "interview_history": st.session_state.interview_history
                                    }
                                )

                                if feedback_response.status_code == 200 and answer_response.status_code == 200:
                                    feedback_data = feedback_response.json()
                                    answer_data = answer_response.json()
                                    
                                    st.session_state.feedback = feedback_data["text"]
                                    
                                    if "example_answers" not in st.session_state:
                                        st.session_state.example_answers = answer_data["text"]
                                    
                                    # 대화 기록과 피드백 저장
                                    save_interview_history()
                                    
                                    st.rerun()
                                else:
                                    st.error("피드백 또는 모범 답변 생성 중 오류가 발생했습니다.")
                                    
                            except Exception as e:
                                st.error(f"오류가 발생했습니다: {str(e)}")
                
                # 피드백이 생성된 경우 피드백과 모범 답변 표시
                if "feedback" in st.session_state:
                    st.markdown("""
                        ### <span class="custom-heading" style="color: #00cbff !important; font-size: 20px !important;">📄 면접 결과</span>
                        """, unsafe_allow_html=True
                    )
                    st.markdown("---")
                    st.markdown("#### 면접 피드백")
                    st.text(st.session_state.feedback)
                    st.markdown("---")
                    
                    st.markdown("#### 모범 답변")
                    st.text(st.session_state.example_answers)
                    st.markdown("---")
                    
                    # 피드백 아래에 다시 시작하기 버튼 표시
                    if st.button("다시 시작하기", use_container_width=True):
                        st.session_state.restart = True
                        st.rerun()

def move_to_next_question():
    """다음 메인 질문으로 이동하는 헬퍼 함수"""
    if (st.session_state.question_index < len(st.session_state.base_questions)):
        next_question = st.session_state.base_questions[st.session_state.question_index]
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": next_question
        })
        
        # 다음 base question과 example answer 저장
        st.session_state.interview_history["question"].append(next_question)
        st.session_state.interview_history["example_answer"].append(
            st.session_state.base_answers[st.session_state.question_index]
        )
        
        st.session_state.question_index += 1
        st.session_state.current_followup_count = 0
    else:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "면접이 모두 종료되었습니다. 수고하셨습니다."
        }) 

def save_interview_history():
    """면접 대화 기록과 피드백을 JSON 파일로 저장"""
    user_id = st.session_state.user["user_id"]
    save_dir = Config.CHAT_HISTORY_PATH + f"{user_id}/"
    os.makedirs(save_dir, exist_ok=True)
    
    # 현재 시간을 파일명에 포함
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 고유 채팅 ID 생성
    chat_id = str(uuid.uuid4())
    filename = f"{save_dir}/{chat_id}.json"
    
    # 저장할 데이터 구성
    save_data = {
        "interview_info": {
            "position": st.session_state.position,
            "experience": st.session_state.experience,
            "datetime": timestamp
        },
        "conversation": {
            "messages": st.session_state.messages
        },
        "feedback": {
            "text": st.session_state.feedback
        },
        "example_answers": {
            "text": st.session_state.example_answers
        }
    }
    
    # JSON 파일로 저장
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"대화 기록 저장 중 오류가 발생했습니다: {str(e)}") 
    
    # DB에 면접 메타데이터 저장
    try:
        metadata = {
            "chat_id": chat_id,
            "user_id": st.session_state.user["user_id"],
            "position": st.session_state.position,
            "experience": st.session_state.experience,
            "timestamp": timestamp
        }
        
        response = requests.post(
            f"{API_URL}/personal/save/chat_history",
            json=metadata
        )
        
        if response.status_code != 200:
            st.warning("면접 메타데이터 저장에 실패했습니다.")
    except Exception as e:
        st.warning(f"메타데이터 저장 중 오류 발생: {str(e)}")