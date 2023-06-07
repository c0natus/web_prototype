import os
import requests
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Optional

with open(os.path.join(os.path.dirname(__file__), 'key'), 'r', encoding='utf-8') as file:
    PRIVATE_KEY = file.read()


class User(BaseModel):
    user: str


class Query(BaseModel):
    query: str


class Coord(BaseModel):
    lat: float
    lng: float


class RecUserInfo(BaseModel):
    user: str
    ca: int
    lat: float
    lng: float
    repeat: bool
    mode: str
    negatives: list
    time_info: Optional[dict] = None


class ItemRating(BaseModel):
    star_num: int
    low_reason: str


class Review(BaseModel):
    user: str
    categories: str
    lat: float
    lng: float
    mode: str
    algo: str
    item_ratings: Any
    keep_using: str
    user_negatives: Optional[list] = None
    opinion: str


app = FastAPI()


@app.get("/notification/")
def notification():
    notices = {
        '개인화 POI 추천 알고리즘 PoC 방법에 대해 안내드립니다.': 
"""개인화 POI 추천 알고리즘 PoC 방법에 대해 안내드립니다.\n\n""" +\
"""아래 총 7가지 평가를 권장해 드리며, 시간과 장소 제약이 따를 경우 '현재 시간'과 '주소 입력'을 통해 추천 받을 시간과 위치를 변경하여 평가 가능합니다.\n\n""" +\
"""최대한 솔직하게 평가자분들의 소중한 의견 부탁드립니다.\n\n""" +\
"""감사합니다.\n\n""" +\
"""※ 본 개인화 POI 추천 알고리즘은 추천 받고자하는 차량 운행 시점의 시간과 위치가 매우 중요하므로, 필요시 차량 탑승 시점과 위치를 가정하여 변경 후 평가 부탁드립니다.\n\n"""+\
"""\n\n"""+\
"""1. 대상 : 인포테인먼트기획팀원 (루첸 상주 인원 중 방문 POI 히스토리가 있는 인원)\n\n"""+\
"""2. PoC 검증 기간 : 5/4 퇴근, 5/6~7 상시, 5/8 출근\n\n"""+\
"""   ※ 5/5일 : 평가 미실시 (알고리즘에 공휴일 반영을 못하여 평가 시 추천 결과가 미흡합니다.)\n\n"""+\
"""3. 평가 방법\n\n"""+\
"""   1\) 차량에 탑승 후 PoC용 모바일 웹페이지 접속\n\n"""+\
"""   2\) 사용자 선택 : 평가자 개인별 이니셜 선택\n\n"""+\
"""   3\) 카테고리 선택 : 시험 항목 별 카테고리 선택\n\n"""+\
"""   > \- 카테고리 : '전체',  알고리즘 : '방문한적 없는 새로운 장소 추천 받기' ⇒ 교통편의/생활편의/여행레저 3개 카테고리 중 추천\n\n"""+\
"""   > \- 카테고리 : '전체',  알고리즘 : '방문한 곳 포함 장소 추천 받기' ⇒ 전체 11개 카테고리 중 추천\n\n\n\n"""+\
"""   4\) 시간선택 : Default '현재 시간' → 자동으로 휴대폰의 현재 시간 정보를 받아옴\n\n"""+\
"""   > \- 추천 받을 시간을 변경하고 싶은 경우 '시간 선택'을 선택한 후 날짜와 시간 ('+' 버튼을 눌러 시간 선택)을 입력\n\n\n\n"""+\
"""   5\) 위치선택 : '현위치' 버튼 입력 시 자동으로 휴대폰의 현재 위치 정보를 받아옴\n\n"""+\
"""   > \- 추천 받을 차량 탑승 위치를 변경하고 싶은 경우 '주소 입력'창에 주소나 POI 명칭을 입력\n\n"""+\
"""   6\) 거리 제한 없이 POI 추천받기 or 주변 (현위치<5km) POI 추천받기를 선택하여 추천을 받고, 리뷰 결과를 입력\n\n"""+\
"""\n\n"""+\
"""     ※ 권장 평가 방법\n\n"""+\
"""    ① 평가#1 : 5/4일 퇴근 시\n\n"""+\
"""   > \- 카테고리 : '전체',  알고리즘 : '방문한 곳 포함 장소 추천 받기'\n\n"""+\
"""    ② 평가#2 : 5/6~7 상시\n\n"""+\
"""   > \- 카테고리 : '전체',  알고리즘 : '방문한적 없는 새로운 장소 추천 받기'\n\n"""+\
"""    ③ 평가#3 : 5/6~7 상시\n\n"""+\
"""   > \- 카테고리 : '교통편의', 알고리즘 : '방문한적 없는 새로운 장소 추천 받기'\n\n"""+\
"""    ④ 평가#4 : 5/6~7 상시\n\n"""+\
"""   > \- 카테고리 : '생활편의', 알고리즘 : '방문한적 없는 새로운 장소 추천 받기'\n\n"""+\
"""    ⑤ 평가#5 : 5/6~7 상시\n\n"""+\
"""   > \- 카테고리 : '여행레저', 알고리즘 : '방문한적 없는 새로운 장소 추천 받기'\n\n"""+\
"""    ⑥ 평가#6 : 5/6~7 상시\n\n"""+\
"""   > \- 카테고리 : '전체',  알고리즘 : '방문한 곳 포함 장소 추천 받기'\n\n"""+\
"""    ⑦ 평가#7 : 5/8 출근\n\n"""+\
"""   > \- 카테고리 : '전체',  알고리즘 : '방문한 곳 포함 장소 추천 받기'""",
        # 'title2': 'content2',
        # 'title3': 'content3',
        # 'title4': 'content4',
        # 'title5': 'content5',
    }

    return notices


@app.post("/query/")
def address_to_coord(data: Query):
    params = {
            'query': data.query 
        }
    header = {
        'Authorization': f'KakaoAK {PRIVATE_KEY}',
    }
    try:
        url = 'https://dapi.kakao.com/v2/local/search/keyword'
        response = requests.get(url, headers=header, params=params).json()

        first_document = response['documents'][0]
        meta = {
            'lat': first_document['y'],
            'lng': first_document['x'],
            'address': first_document['road_address_name'],
            'place_name': first_document['place_name']
        }
    except:
        url = 'https://dapi.kakao.com/v2/local/search/address'
        response = requests.get(url, headers=header, params=params).json()
        first_document = response['documents'][0]

        meta = {
            'lat': first_document['y'],
            'lng': first_document['x'],
            'address': first_document['road_address']['address_name'],
            'place_name': "",
        }

    return meta


def conver_func_coords_to_add(lat, lng):
    url = 'https://dapi.kakao.com/v2/local/geo/coord2address'
    params = {
        'x': lng,
        'y': lat,
    }
    header = {
        'Authorization': f'KakaoAK {PRIVATE_KEY}',
    }

    response = requests.get(url, headers=header, params=params).json()

    try:
        address_name = response['documents'][0]['road_address']['address_name']
        building_name = response['documents'][0]['road_address']['building_name']
        address = f'{address_name} ({building_name})'
    except:
        try:
            address = response['documents'][0]['address']['address_name']
        except:
            address = None    
    return address



@app.post("/coord/")
def coord_to_address(data: Coord):
    return conver_func_coords_to_add(data.lat, data.lng)


def get_user_negatives(user):
    dir_path = os.path.dirname(__file__)
    file_path = os.path.join(dir_path, 'review.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        user_reviews = json.load(file)

    if user in user_reviews.keys(): return user_reviews[user]['user_negatives']
    else: return []


@app.post("/negatives/")
def user_negatives(data: User):
    return get_user_negatives(data.user)


@app.post("/rec/")
def rec(data: RecUserInfo):
    from . import predict
    if data.ca == 0:
        data.ca = 'all'
    info = {
        'user': data.user,
        'lat': data.lat,
        'lng': data.lng,
        'ca': data.ca,
        'repeat': data.repeat,
        'mode': data.mode,
        'user_negatives': data.negatives,
        'time_info': data.time_info
    }
    
    print('*' * 10)
    print(info)
    print('*' * 10)

    rec_list = predict.main(info)
    top_item_city_names = []
    for i in range(len(rec_list['top_item_coors'])):
        lat, lng = rec_list['top_item_coors'][i]
        address = conver_func_coords_to_add(lat, lng)
        if address: top_item_city_names.append(' '.join(list(address.split())[:2]))
        else: top_item_city_names.append('')
    rec_list['top_item_city_names'] = top_item_city_names
    return rec_list


@app.post("/review/")
def review(data: Review):
    user = data.user
    categories = data.categories
    lat = data.lat
    lng = data.lng
    mode = data.mode
    algo = data.algo
    item_ratings = data.item_ratings
    keep_using = data.keep_using
    user_negatives = data.user_negatives
    opinion = data.opinion

    dir_path = os.path.dirname(__file__)
    file_path = os.path.join(dir_path, 'review.json')

    with open(file_path, 'r', encoding='utf-8') as file:
        user_reviews = json.load(file)

    cur_review = {
                'categories': categories,
                'lat': lat,
                'lng': lng,
                'mode': mode,
                'algo': algo,
                'item_ratings': item_ratings,
                'keep_using': keep_using,
                'opinion': opinion,
            }

    if user in user_reviews.keys():
        user_reviews[user]['user_negatives'] = list(set(user_reviews[user]['user_negatives']) | set(user_negatives))
        user_reviews[user]['reviews'].append(cur_review)
    else:
        user_reviews[user] = {
            'user_negatives': list(set(user_negatives)),
            'reviews': [cur_review],
        }

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(user_reviews, file, indent='\t', ensure_ascii=False)


    return '제출 성공'
