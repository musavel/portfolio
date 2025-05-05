import streamlit as st
import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

API_URL = Config.API_URL

def show():
    with st.sidebar:
        if 'user' in st.session_state and st.session_state.user:
            # 현재 로그인된 사용자의 이메일과 저장된 user_info의 이메일이 다르면 user_info 초기화
            if ('user_info' in st.session_state and 
                st.session_state.user_info and 
                st.session_state.user_info['email'] != st.session_state.user['email']):
                st.session_state.user_info = None

            # user_info가 없거나 None일 때만 API 호출
            if 'user_info' not in st.session_state or st.session_state.user_info is None:
                try:
                    response = requests.get(
                        f"{API_URL}/auth/me",
                        headers={"Authorization": f"Bearer {st.session_state.user['access_token']}"}
                    )
                    if response.status_code == 200:
                        st.session_state.user_info = response.json()
                except Exception as e:
                    st.error(f"사용자 정보를 불러오는 중 오류가 발생했습니다: {str(e)}")
                    return

            # 저장된 사용자 정보 표시
            user_info = st.session_state.user_info
            
            st.title("Prompti")
            st.markdown(f"### 🤖 {user_info['email']}")
            st.markdown(f"**회원 유형**: {user_info['user_type']}")
            
            st.markdown("---")
            
            if st.button("로그아웃"):
                st.session_state.clear()
                
                st.rerun()