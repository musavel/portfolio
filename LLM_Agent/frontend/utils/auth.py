import os
import sys

import streamlit as st
import requests
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

API_URL = Config.API_URL

def login(email: str, password: str, user_type: str) -> Optional[dict]:
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "email": email,
                "password": password,
                "user_type": user_type
            }
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"로그인 중 오류가 발생했습니다: {str(e)}")
        return None

def register(email: str, password: str, user_type: str) -> bool:
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={
                "email": email,
                "password": password,
                "user_type": user_type
            }
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"회원가입 중 오류가 발생했습니다: {str(e)}")
        return False

def show_login_page():
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("이메일")
            password = st.text_input("비밀번호", type="password")
            user_type = st.selectbox("회원 유형", ["개인", "기업"])
            submit = st.form_submit_button("로그인")
            
            if submit:
                result = login(email, password, user_type)
                if result:
                    st.session_state.user = result
                    st.rerun()
                else:
                    st.error("이메일 또는 비밀번호가 올바르지 않습니다.")
    
    with tab2:
        with st.form("register_form"):
            email = st.text_input("이메일")
            password = st.text_input("비밀번호", type="password")
            user_type = st.selectbox("회원 유형", ["개인", "기업"])
            submit = st.form_submit_button("회원가입")
            
            if submit:
                if register(email, password, user_type):
                    st.success("회원가입이 완료되었습니다. 로그인해주세요.")
                else:
                    st.error("회원가입 중 오류가 발생했습니다.") 