import streamlit as st
from tabs import home, job_description

def show_company_view():
    tab1, tab2 = st.tabs(["홈", "직무 기술서 생성"])
    
    with tab1:
        home.show()
    with tab2:
        job_description.show() 