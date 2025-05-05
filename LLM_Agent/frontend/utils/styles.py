import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
                
        /* 로고 컨테이너: Flexbox로 가운데 정렬 */
        .logo-container {
            display: flex;
            justify-content: center;
            margin: 20px 0; /* 위아래 여백 필요하면 추가 */
        }
                
        /* Google 폰트 가져오기 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
        
        /* 전역 폰트 적용: 거의 모든 요소에 폰트 강제 지정 */
        .stApp, .stMarkdown, p, h1, h2, h3, div, span, button, input, select, textarea, li, strong, b {
            font-family: 'Noto Sans KR', sans-serif !important;
        }
        /* 배경색 설정 */
        .stApp {
            background-color: #000000ff !important;
        }
        /* 사이드바 배경색과 스타일 변경 */
        [data-testid="stSidebar"] {
            background-color: #212121ff !important;
            border-right: 1px solid #525252ff !important;
        }
        
        /* 사이드바 내 타이틀 스타일 */
        [data-testid="stSidebar"] h1 {
            color: #ffffffff !important; 
            background: linear-gradient(to right, #00cbffff, #f902ffff, #6976ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            font-size: 32px !important;
            border-bottom: 1px solid #525252ff;
            padding-bottom: 15px;
            margin: 8px 0;
        }
        
        /* 사이드바 내 이메일 텍스트 스타일 */
        [data-testid="stSidebar"] h3 {
            color: #f2f0fdff !important;

        }
        
        /* 사이드바 일반 텍스트 스타일 */
        [data-testid="stSidebar"] .stMarkdown p {
            color: #f2f0fdff !important;
        }
        
        /* 사이드바의 이메일 링크 비활성화 */
        [data-testid="stSidebar"] a {
            color: inherit !important;
            text-decoration: none !important;
            pointer-events: none !important;
        }
        
        /* 사이드바 강조 텍스트 스타일 */
        [data-testid="stSidebar"] .stMarkdown strong {
            color: #f2f0fdff !important;
        }
        
        /* 구분선 스타일 */
        [data-testid="stSidebar"] hr {
            border-color: #525252ff !important;
            margin: 1px 0;
        }
        
        /* 로그아웃 버튼 스타일 */
        [data-testid="stSidebar"] button {
            /* 그라데이션 텍스트 효과 */
            background: linear-gradient(to right, #00cbffff, #ff2dffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 500; /* 원한다면 숫자를 높여서 더 두껍게 */

            /* 만약 배경색과 테두리 등 버튼 전체 스타일을 지정하고 싶다면 별도로 적용 */
            border-radius: 20px !important;
            border: 2px solid #525252ff !important;
            padding: 5px 15px !important;
            transition: all 0.3s !important;
        }

        [data-testid="stSidebar"] button:hover {
            box-shadow: 0 0 10px rgba(139, 107, 255, 0.5) !important;
        }

                        
        /* 헤더 스타일 */
        h1, h2, h3 {
            color: #003366 !important;
            font-family: 'Noto Sans KR', sans-serif !important;
        }
        
        /* 문단 스타일 */
        p, .stMarkdown p {
            font-size: 16px !important;
            line-height: 1.6 !important;
            font-family: 'Noto Sans KR', sans-serif !important;
        }
        
        /* 로고 컨테이너 스타일 */
        .logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 2rem;
        }
        
        /* 버튼 및 입력 필드 스타일 */
        .stButton > button, .stTextInput > div > div > input, .stSelectbox > div > div > select {
            font-family: 'Noto Sans KR', sans-serif !important;
        }
        
        /* styles.py 내부 예시 */
        .chatbot-title {
            font-size: 20px !important; /* 원하는 크기 */
            color: #ff00ff !important;  /* 원하는 색상 */
            font-weight: 700 !important;
            /* 그라데이션 텍스트도 가능!
            background: linear-gradient(to right, #00cbff, #ff2dff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            */
        }



        </style>
    """, unsafe_allow_html=True)