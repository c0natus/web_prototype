import os
import time
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_star_rating import st_star_rating
import streamlit.components.v1 as components
import extra_streamlit_components as stx
import requests


def init_setting():
    st.set_page_config(initial_sidebar_state='collapsed')
    with open(os.path.join(os.path.dirname(__file__), 'rec_style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    return stx.CookieManager()


# def star_rating(idx, height):
#     with open(os.path.join(os.path.dirname(__file__), f'star{idx}_rating.html')) as f:
#         components.html(f.read(), height=height)


@st.cache_data(show_spinner='Wait...')
def do_rec(data, time):
    rec_list = requests.post(url=f'http://141.223.163.115:8000/rec/', json=data).json()
    return rec_list


def get_data_dict(cookie_manager):
    user = 1 # cookie_manager.get('user')

    categories = cookie_manager.get('categories')
    if categories == '전체': ca = 0
    elif categories == '교통편의': ca = 1
    elif categories == '생활편의': ca = 2
    elif categories == '여행레저': ca = 3
    else:
        ca = 0 
        st.write('Not supported category')

    algo = cookie_manager.get('algo')
    if algo == '반복 POI 추천': repeat = True
    elif algo == '신규 POI 추천': repeat = False
    else:
        repeat = True 
        st.write('Not supported algo.')
    
    lat = cookie_manager.get('lat') # 36.621677
    lng = cookie_manager.get('lng') # 127.486930
    mode = cookie_manager.get('mode')

    data = {
        'user': user,
        'ca': ca,
        'lat': lat,
        'lng': lng,
        'repeat': repeat,
        'mode': mode
        }

    return data


def display_rec_list(rec_list):
    st.markdown('---')
    star_ratings = [None] * 5
    low_reasons = [None] * 5
    for i in range(5):
        with st.container():
            item_name_col, star_col = st.columns([8, 2])
            _, idx_col1, idx_col2 = st.columns([0.3, 5, 5])
            _, idx_col3 = st.columns([0.3, 10])
            with item_name_col:
                city_place = f"{rec_list['top_item_city_names'][i]} {rec_list['top_item_names'][i]}"
                st.write(f"{i+1}. [{city_place}](<https://map.naver.com/v5/search/{city_place}>)")
            with star_col:
                star_ratings[i] = st_star_rating(label='', maxValue=5, defaultValue=3, size=20, key=f"rating{i+1}")
                # star_rating(i+1, 27)
            with idx_col1:
                st.write(f"거리: {rec_list['top_item_distances'][i]} km")
            with idx_col2:
                st.write(f"추천 점수: {rec_list['top_item_scores'][i]}")
            with idx_col3:
                st.write(f"추천 이유: {rec_list['top_item_descriptors'][i]}")
            
            low_reasons[i] = st.text_area(
                label=f'item{i+1}', 
                placeholder="별점이 낮은 이유는 무엇인가요?",
                label_visibility='collapsed')
            st.markdown('---')

    return star_ratings, low_reasons


def display_review():
    keep_using_text, keep_using_check = st.columns([7,3])
    with keep_using_text: st.write("실제 서비스로 나올 경우 계속 쓸 용의가 있는가요?")
    with keep_using_check:
        keep_using = st.selectbox(
            label='keep_using', 
            options=['Y', 'N'],
            label_visibility="collapsed")

    not_rec_cand = (1, 2, 3, 4, 5)
    user_negatives_list = st.multiselect(
        label="not_rec", 
        options=not_rec_cand,
        label_visibility="collapsed")
    
    opinion = st.text_area(
        label="opinion",
        placeholder="전반적인 추천 결과에 대한 의견은?",
        label_visibility="collapsed",
    )
    
    return keep_using, user_negatives_list, opinion


def main():
    cookie_manager = init_setting()
    title_col, _, descriptor_col = st.columns([4, 0.5, 5])
    with title_col:
        st.header("추천 결과 확인")
        if st.button("홈"): switch_page("home")
    with descriptor_col:
        with open(os.path.join(os.path.dirname(__file__), f'star_descriptor.html')) as f:
                components.html(f.read(), height=158)
    with open(os.path.join(os.path.dirname(__file__), 'rec_style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    data = get_data_dict(cookie_manager)    
    rec_list = do_rec(data, time.time() // 3600,)

    star_ratings, low_reasons = display_rec_list(rec_list)
    keep_using, user_negatives_list, opinion = display_review()

    item_ratings = {}
    for i in range(5):
        item_ratings[rec_list['top_items'][i]] = {
            'star_num': star_ratings[i],
            'rec_score': rec_list['top_item_scores'][i],
            'distance': rec_list['top_item_distances'][i],
            'low_reason': low_reasons[i],
        }

    review_data = {
        'user': data['user'],
        'categories': data['ca'],
        'lat': data['lat'],
        'lng': data['lng'],
        'mode': data['mode'],
        'algo': data['repeat'],
        'item_ratings': item_ratings,
        'keep_using': keep_using,
        'user_negatives': [rec_list['top_items'][int(i)-1] for i in user_negatives_list],
        'opinion': opinion,
    }

    if st.button('제출하기'):
        result = requests.post(url='http://141.223.163.115:8000/review/', json=review_data).json()
        st.write(result)

main()