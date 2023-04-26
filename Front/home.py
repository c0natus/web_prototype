import os
import time
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.switch_page_button import switch_page
import extra_streamlit_components as stx



def init_setting():
    st.set_page_config(initial_sidebar_state='collapsed')
    with open(os.path.join(os.path.dirname(__file__), 'home_style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    return stx.CookieManager()


def notification():
    noti_col, _ = st.columns([5,5])
    with noti_col:
        if st.button("공지사항"):
            switch_page("notification")


def user_select():
    user_list = ['사용자 선택', 'CHW_MyCar',  'HSK_MyCar', 'JJK', 'KBH', 'KHY', 'KYJ', 'LHS', 'MJH', 'MJH_MyCar', 'OSM']
    
    user = st.selectbox(
        label='user_select', 
        options=user_list,
        label_visibility="collapsed")

    return user


def categories_select():
    categories_list = ('카테고리 선택', '전체', '교통편의', '생활편의', '여행레저')
    categories = st.selectbox(
        label="categories_select",
        options=categories_list,
        label_visibility="collapsed",
    )

    # categories = st.multiselect(
    #     label="categories_select", 
    #     options=categories_list,
    #     label_visibility="collapsed")

    return categories


def algo_select():
    algo_list = ['알고리즘 선택', '방문한적 없는 새로운 장소 추천 받기', '방문한 곳 포함 장소 추천 받기']

    algo = st.selectbox(
        label='algo_select',
        options=algo_list,
        label_visibility="collapsed")

    return algo


def get_current_location(cookie_manager):
    with open(os.path.join(os.path.dirname(__file__), 'current_location.html')) as f:
        components.html(f.read(), height=0)
    
    default_lat = cookie_manager.get('cur_lat')
    default_lng = cookie_manager.get('cur_lng')
    
    if cookie_manager.get('enable_cur_loc') in ['0', None]: 
        err_msg = True
        default_lat = 37.5662952
        default_lng = 126.9779451
    else:
        err_msg = False
    
    return default_lat, default_lng, err_msg


def clear_text(key: str):
    st.session_state[key] = ""


def get_location(cookie_manager):
    st.write("위치")
    col_cur, col_query = st.columns(2)
    col_lat, col_lng = st.columns(2)
    container = st.container()

    default_lat = None
    default_lng = None
    address = None

    default_lat, default_lng, err_msg = get_current_location(cookie_manager)

    with col_cur:
        cur_location = st.button("현위치", on_click=clear_text, args=("query", ))
    with col_query:
        query = st.text_input(
            "주소 입력",
            placeholder="주소 입력: ", 
            label_visibility="collapsed",
            key="query")
        
    if cur_location:  
        default_lat, default_lng, err_msg = get_current_location(cookie_manager)
    
    if query:
        data = {
            'query': query,
            # 'key': st.secrets["KakaoAK"]
        }
        try:
            meta = requests.post(url='http://141.223.163.115:8000/query/', json=data).json()
            default_lat = meta['lat']
            default_lng = meta['lng']
            address = meta['address']
            place_name = meta['place_name']
            address = f"{address} ({place_name})"
        except:
            st.write("주소를 다시 입력해주세요.")
    
    if address is None:
        data = {
            'lat': default_lat,
            'lng': default_lng,
            # 'key': st.secrets["KakaoAK"]
        }

        address = requests.post(url='http://141.223.163.115:8000/coord/', json=data).json()

    with col_lat:
        lat = st.number_input(
            "위도", 
            min_value=-90., 
            max_value=90., 
            value=float(default_lat), 
            step=0.0000001,
            format="%.7f"
            )
    with col_lng:
        lng = st.number_input(
            "경도", 
            min_value=-180., 
            max_value=180., 
            value=float(default_lng), 
            step=0.0000001,
            format="%.7f",
            )

    cookie_manager.set('lat', lat, key='lat')
    cookie_manager.set('lng', lng, key='lng')

    if address: container.write(address)
    if err_msg: container.write('현재 위치를 받아올 수 없습니다.')


def check_and_change_page(user, categories, algo, mode, cookie_manager):
    if user == '사용자 선택': st.write('사용자를 선택하세요.')
    elif categories == '카테고리 선택': st.write('카테고리를 선택하세요')
    elif algo == '알고리즘 선택': st.write('알고리즘을 선택하세요')
    else: 
        cookie_manager.set('mode', mode, key='mode')
        for i in range(100):
            if cookie_manager.get('mode') != mode: time.sleep(0.01)
            else: break
        switch_page('rec')


def rec_dest(user, categories, algo, cookie_manager):
    if st.button('거리 제한 없이 POI 추천 받기', key='dest'):
        check_and_change_page(user, categories, algo, 'default', cookie_manager)


def rec_near(user, categories, algo, cookie_manager):
    if st.button('주변 (현위치<5km) POI 추천 받기', key='near'):
        check_and_change_page(user, categories, algo, 'near', cookie_manager)


def main():
    cookie_manager = init_setting()
    st.title("개인화 POI 추천 알고리즘 PoC")
    notification()
    
    user = user_select()
    categories = categories_select()
    algo = algo_select()
    get_location(cookie_manager)

    cookie_manager.set('user', user, key='user')
    cookie_manager.set(cookie='categories', val=categories, key='categories')
    cookie_manager.set('algo', algo, key='algo')

    rec_dest(user, categories, algo, cookie_manager)
    rec_near(user, categories, algo, cookie_manager)


main()