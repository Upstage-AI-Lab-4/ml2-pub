from fastapi import FastAPI, Query
import model_server
from model_server import ModelType
import json
from typing import Optional, Annotated, List
from pydantic import BaseModel


app = FastAPI()

class StringArrayInput(BaseModel):
    movies: List[str] 
    ratings: List[str]

@app.get("/")
async def root():
    return {
        "message": "Hello World!"
    }

@app.get("/help/")
async def help():
    return {
        "message": "This is our First Movie Recommend System"
    }

#User Id 정보를 확인하여 기존에 존재하는지 아닌지를 반환
@app.get("/user/exist/{user_id}")
async def is_user_exist(user_id: str):
    ret = model_server.isExistUserId(user_id)
    result = {"user_id":user_id,"exist":ret}
    print(result)
    return result

#User ID를 새로 생성 후 반환
@app.post("/user/create/")
async def crete_user():
    user_id = model_server.createUser()
    result = {"user_id":user_id, "status":True}
    print("Create Success")
    return result

#User ID를 통해 로그인 후 성공여부 반환
@app.post("/user/login/{user_id}")
async def login(user_id):
    ret = model_server.login(user_id)
    result = {"user_id":str(user_id), "status":ret}
    print(result)
    return result

@app.get("/user/currentId/")
async def get_id():
    id = model_server.get_currentId()
    result = {"user_id":id}
    print(f"Current Id : {model_server.get_currentId()}")
    return result


####Cold Start 해결을 위한 Movie List 가져오고 Movie Rate List 올려주기

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
@app.get("/list/movie/recommend/")
async def movie_recommend(type:ModelType = ModelType.UserBased, num_recommend = 10):
    ret_1, ret_2 = model_server.get_recommend(type, num_recommend)
    result = {"items":ret_1, 'ratings':ret_2}
    print(result)
    return result



