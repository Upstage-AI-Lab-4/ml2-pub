import os
os.sys.path.append('src')

from fastapi import FastAPI
from fastapi import Request

import pickle
import tag

app = FastAPI()
storage = dict()

@app.get("/")
async def root():
    return {
        "message": "Hello World!"
    }

@app.get("/movie_recommend/{user_id}")
async def movie_recommend(user_id: str, type = None, num_recommend = 10):
    print((user_id, type, num_recommend))
    if not 'model' in storage:
        return {
            'message': 'model is not ready'
        }

    return {
        "message": "movie_recommend",
        "payload": (user_id, type, num_recommend)
    }

@app.post("/set_first_rate/{user_id}/{movie_id}/{ratings}")
async def set_first_rate(user_id: str, movie_id: str, ratings: int):
    print((user_id, movie_id, ratings))
    return {
        "message": "movie_recommend",
        "payload": (user_id, movie_id, ratings)
    }

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

