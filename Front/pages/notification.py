import os
import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page
import extra_streamlit_components as stx

def init_setting():
    st.set_page_config(initial_sidebar_state='collapsed')
    # with open(os.path.join(os.path.dirname(__file__), os.pardir, 'home.css')) as f:
    with open(os.path.join(os.path.dirname(__file__), 'rec_style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    return stx.CookieManager()

def main():
    cookie_manager = init_setting()
    
    datas = requests.get(url='http://141.223.163.115:8000/notification').json()

    st.title("공지사항")
    if st.button("홈"): switch_page("home")

    for key, value in datas.items():
        with st.expander(key):
            st.write(value)


main()