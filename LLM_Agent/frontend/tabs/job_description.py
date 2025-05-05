import os
import sys

import streamlit as st
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

API_URL = Config.API_URL

def show():
    # 세션 상태 초기화
    if 'jd_result' not in st.session_state:
        st.session_state.jd_result = None
    if 'interview_questions' not in st.session_state:
        st.session_state.interview_questions = None
        
    st.markdown("""
        ### <span class="custom-heading" style="color: #00cbff !important; font-size: 20px !important;">📑 직무 기술서 생성</span>
        채용하고자 하는 포지션에 대한 상세한 기술서를 자동으로 생성할 수 있습니다.
        """, unsafe_allow_html=True
    )
    
    # 직무 정보 입력
    with st.form("job_description_form"):
        position = st.selectbox("채용 포지션", ["포지션 선택", "데이터 분석가", "데이터 엔지니어", "머신러닝 엔지니어", "AI 엔지니어", "AI 연구원"])
        experience = st.selectbox("경력 요구 사항", ["신입", "1-3년", "3-5년", "5-10년", "10년이상"])

        submitted = st.form_submit_button("기술서 생성", use_container_width=True)
    
    if position != "포지션 선택" and submitted:
        try:
            # API 요청
            with st.spinner("선택하신 정보로 직무 기술서를 생성중 입니다..."):
                response = requests.post(
                    f"{API_URL}/company/generate/description",
                    json={
                        "position": position,
                        "experience": experience
                    }
                    , headers={"Authorization": f"Bearer {st.session_state.user['access_token']}"}
                )
                
                if response.status_code == 200:
                    st.session_state.interview_questions = False
                    st.session_state.jd_result = response.json()
                else:
                    st.error("기술서 생성 중 오류가 발생했습니다.")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
    
                
    # JD 결과가 있으면 표시
    if st.session_state.jd_result:
        st.markdown("""
            ### <span class="custom-heading" style="color: #00cbff !important; font-size: 20px !important;">📝 생성된 직무 기술서</span>
            """, unsafe_allow_html=True
        )
        jd_text = st.text_area("<직무 기술서>", st.session_state.jd_result["text"], height=500)

        col1, col2 = st.columns(2)
        
        with col1:
            if st.download_button(
                label="기술서 저장",
                data=jd_text,
                file_name=f"직무기술서_{position}_{experience}.txt",
                mime="text/plain",
                use_container_width=True
            ):
                st.success("직무 기술서가 다운로드되었습니다.")
        
        with col2:            
            if st.button("면접 질문 생성", key='generate_questions', use_container_width=True):
                try:
                    with st.spinner("선택하신 정보로 추천 면접 질문을 생성중 입니다..."):
                        interview_response = requests.post(
                            f"{API_URL}/company/generate/question",
                            json={
                                "position": position,
                                "experience": experience,
                                "num": Config.QUESTION_NUM
                            },
                            headers={"Authorization": f"Bearer {st.session_state.user['access_token']}"}
                        )
                        
                        if interview_response.status_code == 200:
                            st.session_state.interview_questions = interview_response.json()
                            # st.session_state.generate_questions_clicked = False
                        else:
                            st.error("면접 질문 생성 중 오류가 발생했습니다.")
                except Exception as e:
                    st.error(f"면접 질문 생성 중 오류가 발생했습니다: {str(e)}")
    
    # 면접 질문 결과가 있으면 표시
    if st.session_state.interview_questions:
        st.markdown("""
            ### <span class="custom-heading" style="color: #00cbff !important; font-size: 20px !important;">❓ 추천 면접 질문</span>
            """, unsafe_allow_html=True
        )
        st.text_area("<면접 질문>", st.session_state.interview_questions["text"], height=350)