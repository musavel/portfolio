import streamlit as st

def show():
    # 사용자 세션 확인
    if 'user' not in st.session_state or not st.session_state.user:
        st.rerun()
        return

    st.markdown("""
        <style>
        /* Google 폰트 가져오기 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        
        /* 전역 폰트 적용: 거의 모든 요소에 폰트 강제 지정 */
        * {
            font-family: 'Noto Sans KR', sans-serif !important;
        }
        .stApp {
            
            background-color: #090417ff;
        }
        h1 {
            color: #003366;
        }
        .stMarkdown p {
            font-size: 16px;
            line-height: 1.6;
        }
        /* 제목 전용 스타일: '안녕하세요!'와 '주요 기능', '시작하기'에 적용 */
        .custom-heading {
            color: #00cbffff; /* 원하는 색상으로 변경 (예: 빨간색) */
        }
        </style>
        """, unsafe_allow_html=True
    )
    
    # 컨텐츠를 container 안에 배치
    with st.container():
        if st.session_state.user['user_type'] == '개인':
            st.markdown("""
            ### <span class="custom-heading">👋 안녕하세요!</span>
            
            - Prompti는 AI 기반 가상 면접 시스템입니다.  
            - 실제 면접과 유사한 환경에서 면접 연습을 할 수 있습니다.
            
            ### <span class="custom-heading">🎯 주요 기능</span>
            - **가상 면접 챗봇**: AI 면접관과 실시간 대화  
            - **맞춤형 피드백**: 면접 답변에 대한 AI의 피드백  
            - **대화 기록 확인**: 이전 면접 연습 기록 확인  
            
            ### <span class="custom-heading">🚀 시작하기</span>
            - 상단의 "가상 면접 챗봇" 탭을 클릭하여 면접 연습을 시작하세요.
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            ### <span class="custom-heading">👋 안녕하세요!</span>
            
            - Prompti는 AI 기반 직무 기술서 생성 시스템입니다.  
            - 직무에 대한 상세한 기술서를 자동으로 생성할 수 있습니다.
            
            ### <span class="custom-heading">🎯 주요 기능</span>
            - **직무 기술서 생성**: AI가 직무에 맞는 기술서를 자동 생성  
            - **맞춤형 면접 질문 생성**: 작성된 직무 기술서를 기반으로 면접 질문 생성  
            
            ### <span class="custom-heading">🚀 시작하기</span>
            - 상단의 "직무 기술서 생성" 탭을 클릭하여 기술서 생성을 시작하세요.
            """, unsafe_allow_html=True)