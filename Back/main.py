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
        'title1': 'content1',
        'title2': 'content2',
        'title3': 'content3',
        'title4': 'content4',
        'title5': 'content5',
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