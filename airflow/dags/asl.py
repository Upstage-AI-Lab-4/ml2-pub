from datetime import datetime

import requests
import pandas as pd
import numpy as np
import tag

from sklearn.metrics.pairwise import cosine_similarity 
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix

def handler(movie_dt, rating_dt):
    def create_user_item_matrix(rating_dt):
        # 사용자와 아이템(영화)의 고유 ID를 인덱스로 변환
        user_ids = rating_dt['userId']#.astype('category').cat.codes
        movie_ids = rating_dt['tmdbId']#.astype('category').cat.codes
        ratings = rating_dt['rating'].values

        # csr_matrix 생성
        user_item_matrix = csr_matrix((ratings, (user_ids, movie_ids)))

        return user_item_matrix, user_ids, movie_ids

    # 사용자-아이템 행렬 생성
    user_item_matrix, user_ids, movie_ids = create_user_item_matrix(rating_dt)

    # 생성된 csr_matrix 정보 출력
    print(f"User-Item Matrix shape: {user_item_matrix.shape}")
    print(f"Number of users: {user_item_matrix.shape[0]}, Number of movies: {user_item_matrix.shape[1]}")

    print('create ALS model')
    model = AlternatingLeastSquares(factors=10, regularization=0.8, iterations=40)
    model.fit(user_item_matrix)
    
    return tag.ALSWrapper(model)
