import os
os.sys.path.append('src')

from fastapi import FastAPI
from fastapi import Request

import pickle
import tag
from fastapi import FastAPI, Query
import model_server
import json
from typing import Optional, Annotated, List
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()
storage = dict()

class StringArrayInput(BaseModel):
    movies: List[str] 
    ratings: List[str]

#ID 생성 후 첫 로그인 시 콜드스타트 방지를 위해 평점 메길 첫 영화 리스트 반환
@app.get("/list/movie/firstlist/")
async def get_movielist_for_coldstart():
    ret = model_server.get_movielist_for_coldstart()
    result = {"movie_list":ret}
    print(result)
    return result

#ID 생성 후 첫 로그인 시 반환받은 영화리스트에 평점을 함께 보내서 유저 평점 테이블을 업데이트
@app.post("/set_first_rate/")
async def set_first_rate(input: StringArrayInput):
    model_server.set_first_ratings(input.movies, input.ratings)
    result = {"status":True}
    print(result)
    return result


####TODO: 영화추천하고, 추천받은 페이지에서 또 평점메길수 있게 해서 업데이트

# 추천받기
@app.get("/list/movie/recommend/{type}")
async def movie_recommend(type, num_recommend = 10):
    ret_1, ret_2 = model_server.get_recommend(int(type), num_recommend)
    
    result = {"items":ret_1, 'ratings':ret_2}
    print(result)
    return result





@app.post("/experiment/{experiment_name}/version")
async def set_version(request: Request, experiment_name: str):
    data = await request.json()

    print('request', data)
    source = data['source'].split(':')[1][1:-6]
    model_path = f'/mlartifacts/{source}/{experiment_name}/python_model.pkl'
    print('try to load', model_path)

    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
            storage['model'] = model
            storage['version'] = data['version']
            model_server.load_new_model(model)
            print('model is updated')

        return {
            "message": "set_version",
            # "payload": (model, version)
        }
    except Execept as e:
        print(f'error {e}')
        return {
            "message": "error"
        }

@app.get("/experiment/{experiment_name}/version")
async def get_version(experiment_name: str):
    if not 'version' in storage:
        return {
            'message': 'model is not ready'
        }
        
    return {
        "message": "function: get_version",
        "payload": storage['version']
    }

