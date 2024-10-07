from fastapi import FastAPI


app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "Hello World!"
    }

@app.get("/movie_recommend/{user_id}")
async def movie_recommend(user_id: str, type = None, num_recommend = 10):
    print((user_id, type, num_recommend))
    return {
        "function": "movie_recommend",
        "payload": (user_id, type, num_recommend)
    }

@app.post("/set_first_rate/{user_id}/{movie_id}/{ratings}")
async def set_first_rate(user_id: str, movie_id: str, ratings: int):
    print((user_id, movie_id, ratings))
    return {
        "function": "movie_recommend",
        "payload": (user_id, movie_id, ratings)
    }

