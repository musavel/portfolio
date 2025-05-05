import streamlit as st
import utils.auth as auth
import utils.sidebar as sidebar
from utils.personal import show_personal_view
from utils.company import show_company_view
from utils.styles import apply_styles

# 페이지 설정
st.set_page_config(
    page_title="Prompti",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_styles()

st.markdown("""
    <style>
    /* Streamlit 탭 버튼 간 간격 조정 */
    [data-baseweb="tab"] {
        margin-right: 13px !important;
    }

    /* 탭에 마우스 오버 시 텍스트 색상 */
    [data-baseweb="tab"]:hover {
        color: #dd5463ff !important; /* 예: 주황색 */
    }

    /* 선택된(활성화된) 탭 텍스트 및 밑줄(테두리) 색상 */
    [data-baseweb="tab"][aria-selected="true"] {
        color: #dd5463ff !important; /* 예: 주황색 */
        border-bottom: 2px solid #dd5463ff !important; /* 두께, 색상 조정 가능 */
    }
    </style>
    """, unsafe_allow_html=True
)

st.markdown("""<div style="display: table; margin: 0 auto;">""", unsafe_allow_html=True)
st.image("frontend/prompti_neon.png", width=400)
st.markdown("""</div>""", unsafe_allow_html=True)

def main():
    # 세션 상태 초기화
    if 'user' not in st.session_state:
        st.session_state.user = None
        
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

    # 로그인하지 않은 경우
    if not st.session_state.user:
        st.session_state.initialized = False
        auth.show_login_page()
        return

    # 로그인 직후 첫 렌더링
    if not st.session_state.initialized and st.session_state.user:
        st.session_state.initialized = True
        st.rerun()
        return
    
    # 메인 페이지 표시
    sidebar.show()
    
    # placeholder를 사용하여 탭 컨테이너 생성
    tab_container = st.container()
    
    with tab_container:
        if st.session_state.user['user_type'] == '개인':
            show_personal_view()
        else:  # 기업 사용자
            show_company_view()

if __name__ == "__main__":
    main()