import pickle
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix,vstack

from enum import Enum,auto

class ModelType(Enum):
    UserBased = auto()

with open('saved_model.pkl', 'rb') as f:
    model = pickle.load(f)
    print("Model Loaded!")

movie_path = '../datasets/movies_metadata.csv'
rating_path = '../datasets/ratings.csv'
movie_dt = pd.read_csv(movie_path, low_memory=False)
rating_dt = pd.read_csv(rating_path,low_memory=False)

is_first_login = True
first_list_movies = []
first_list_ratings = []
# CSR 형식으로 변환
user_item_matrix = csr_matrix((rating_dt['rating'], (rating_dt['userId'], rating_dt['movieId'])))


def isExistUserId(user_id):
    if len(rating_dt[rating_dt['userId']==int(user_id)]) > 0:
        return True
    else:
        return False
    
def createUser():
    global current_user_id
    current_user_id = rating_dt['userId'].max()+1
    return str(current_user_id)

def login(user_id):
    global current_user_id
    current_user_id = user_id
    print('Log In Success')
    return True

def get_currentId():
    return str(current_user_id)


def get_movielist_for_coldstart():
    result = []

    unique_genres = ['Action', 'Fantasy', 'Animation', 'Horror', 'Thriller', 'Comedy', 'Romance', 'Drama']

    for genre in unique_genres:
    # 해당 장르의 인기 영화 중에서 하나 선택
        popular_movie = movie_dt[movie_dt['genres'].str.contains(genre)].nlargest(2, 'revenue')
        result.append(popular_movie)

    result_list = pd.concat(result)
    result_list = result_list.drop_duplicates().head(10)
    global first_list_movies
    first_list_movies = result_list.index.astype(str).to_list()
    return first_list_movies

new_user_vector = []
def set_first_ratings(movie_id, ratings):
    print(f"Set First Movies: {movie_id}")
    print(f"Set First Ratings: {ratings}")
    new_user_ratings = {
        'userId': int(current_user_id),
        'movieId': movie_id,
        'rating': ratings  # 유저가 입력한 평점
    }
    # DataFrame으로 변환
    new_ratings_df = pd.DataFrame(new_user_ratings)
    existing_movie_ids = user_item_matrix.shape[1]
    # 신규 유저 평점 벡터 생성
    new_user_vector = np.zeros(existing_movie_ids)
    # 신규 유저의 평점을 벡터에 채워넣기
    for _, row in new_ratings_df.iterrows():
        movie_index = row['movieId']  # 영화 ID
        new_user_vector[movie_index] = row['rating']  # 평점 입력

    ## 새로운 유저 벡터를 2차원 형태로 변환 (1 x 영화 개수)
    #new_user_vector_2d = np.reshape(new_user_vector, (1, -1))
    ### csr_matrix로 변환
    #new_user_csr = csr_matrix(new_user_vector_2d)
    ### 기존 행렬에 새로운 유저 벡터 추가
    #user_item_matrix = vstack([user_item_matrix, new_user_csr])

def get_recommend(type, num_recommend):
    if type == ModelType.UserBased:
        rec_movi_list = recommend_movie_by_als(int(current_user_id), n_movies=int(num_recommend))
        return rec_movi_list

#유저 아이디를 입력하면 다섯개의 추천 목록을 뽑아준다.
def recommend_movie_by_als(user_id, n_movies=5):
    print(f'User id: {user_id}, n_movies={n_movies}')
    print(type(user_id))
    print(type(n_movies))
    if user_id > rating_dt['userId'].max():
        recommendations = model.recommend(0, csr_matrix(new_user_vector), N=n_movies)
    else:
        recommendations = model.recommend(user_id, user_item_matrix[user_id], N=n_movies)
    movie_arr = []
    rating_arr = []
    for idx in recommendations[0]:
        movie_arr.append(str(idx))

    for idx in recommendations[1]:
        rating_arr.append(str(idx))

    return movie_arr,rating_arr
    
