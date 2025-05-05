import streamlit as st
from tabs import home, chat, history

def show_personal_view():
    tab1, tab2, tab3 = st.tabs(["홈", "가상 면접 챗봇", "대화 기록"])
    
    with tab1:
        home.show()
    with tab2:
        chat.show()
    with tab3:
        history.show() 