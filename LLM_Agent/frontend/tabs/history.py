import os
import sys
import streamlit as st
import requests
from datetime import datetime
from utils.styles import apply_styles

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

API_URL = Config.API_URL

def show():
    st.markdown("""
        ### <span class="custom-heading" style="color: #00cbff !important; font-size: 20px !important;">📑면접 기록</span>
        
        지금까지 진행했던 면접 기록을 확인할 수 있습니다.

        """, unsafe_allow_html=True
    )
    
    if "loaded_history" not in st.session_state:
        st.session_state.loaded_history = False
    if "selected_chat" not in st.session_state:
        st.session_state.selected_chat = None
    if "history_data" not in st.session_state:
        st.session_state.history_data = None
        
    # 사용자의 면접 기록 가져오기
    if "user" in st.session_state and st.session_state.user:
        user_id = st.session_state.user["user_id"]
        
        if st.button("나의 면접 기록 조회하기"):
            st.session_state.loaded_history = True
            st.session_state.history_data = None  # 데이터 초기화
            st.markdown("---")
            
        if st.session_state.loaded_history:
            try:
                # history_data가 없을 때만 API 호출
                if st.session_state.history_data is None:
                    response = requests.get(f"{API_URL}/personal/get/chat_history/{user_id}")
                    
                    if response.status_code == 200:
                        st.session_state.history_data = response.json()
                        if not st.session_state.history_data:
                            st.error("아직 저장된 면접 기록이 없습니다.")
                    else:
                        st.error("면접 기록을 불러오는데 실패했습니다.")
                
                # history_data가 있는 경우에만 처리
                if st.session_state.history_data:
                    # Selectbox용 옵션 생성
                    # 날짜 형식을 보기 좋게 변환하는 함수
                    def format_datetime(datetime_str):
                        try:
                            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                            return dt.strftime("%Y년 %m월 %d일 %H:%M")
                        except:
                            return datetime_str
                    
                    st.markdown("""
                        ### <span class="custom-heading" style="color: #00cbff !important; font-size: 20px !important;">📁 면접 기록 선택</span>
                        """, unsafe_allow_html=True
                    )
                    options = [f"{interview['position_name']} / {interview['experience']} / {format_datetime(interview['created_at'])}" for interview in st.session_state.history_data]
                    selected_interview = st.selectbox("면접 기록을 선택하세요", options)
                    st.markdown("---")
                    
                    # 선택된 면접이 변경되었는지 확인
                    if "previous_selection" not in st.session_state:
                        st.session_state.previous_selection = None
                    
                    # 선택이 변경되었으면 상태 초기화
                    if st.session_state.previous_selection != selected_interview:
                        st.session_state.previous_selection = selected_interview
                        st.session_state.loading_detail = True
                        st.session_state.chat_data = None  # 데이터 초기화
                        
                    st.session_state.selected_chat = selected_interview
                    
                    # 선택된 면접 찾기
                    selected_idx = options.index(selected_interview)
                    selected_chat_id = st.session_state.history_data[selected_idx]['id']
                    
                    # 데이터 로딩 중이거나 데이터가 없는 경우
                    if st.session_state.loading_detail or "chat_data" not in st.session_state or st.session_state.chat_data is None:
                        with st.spinner("면접 기록을 불러오는 중입니다..."):
                            try:
                                detail_response = requests.get(
                                    f"{API_URL}/personal/get/chat_content/{user_id}/{selected_chat_id}"
                                )
                                
                                if detail_response.status_code == 200:
                                    st.session_state.chat_data = detail_response.json()
                                    st.session_state.loading_detail = False
                                else:
                                    st.error("면접 상세 내용을 불러오는데 실패했습니다.")
                                    st.session_state.loading_detail = False
                            except Exception as e:
                                st.error(f"오류가 발생했습니다: {str(e)}")
                                st.session_state.loading_detail = False
                    
                    # 데이터가 로딩되었고 사용 가능한 경우에만 표시
                    if not st.session_state.loading_detail and st.session_state.chat_data is not None:
                        chat_data = st.session_state.chat_data
                        
                        # 면접 정보 표시
                        with st.container():
                            st.markdown("""
                                ### <span class="custom-heading" style="color: #00cbff !important; font-size: 20px !important;">🔎 면접 정보</span>
                                 """, unsafe_allow_html=True
                            )
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown(f"**직무:** {chat_data['info']['position']}")
                            with col2:
                                st.markdown(f"**경력:** {chat_data['info']['experience']}")
                            with col3:
                                st.markdown(f"**일시:** {chat_data['info']['datetime']}")
                            st.markdown("---")
                        
                        # 대화 내용과 피드백을 위아래로 나누어 표시
                        
                        # 대화 내용 컨테이너
                        with st.container():
                            st.markdown("""
                                ### <span class="custom-heading" style="color: #00cbff !important; font-size: 20px !important;">💬 대화 내용</span>
                                 """, unsafe_allow_html=True
                            )
                            
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
                            
                            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                            for message in chat_data['messages']:
                                message_class = "assistant-message" if message["role"] == "assistant" else "user-message"
                                st.markdown(
                                    f'<div class="message {message_class}">{message["content"]}</div>',
                                    unsafe_allow_html=True
                                )
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)
                            st.markdown("---")
                        
                        # 피드백 컨테이너
                        with st.container():
                            st.markdown("""
                                ### <span class="custom-heading" style="color: #00cbff !important; font-size: 20px !important;">✅ 면접 피드백</span>
                                 """, unsafe_allow_html=True
                            )
                            st.text(chat_data['feedback'])
                            st.markdown("---")
                            
                        # 모범 답변 컨테이너
                        with st.container():
                            st.markdown("""
                                ### <span class="custom-heading" style="color: #00cbff !important; font-size: 20px !important;">📖 모범 답변</span>
                                 """, unsafe_allow_html=True
                            )
                            st.text(chat_data['example_answers'])
                            st.markdown("---")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
    else:
        st.warning("로그인이 필요합니다.")