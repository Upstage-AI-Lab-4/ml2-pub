import pickle
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix,vstack
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import ast



with open('real_als_model.pkl', 'rb') as f:
    model = pickle.load(f)
    print("Model Loaded!")

def load_new_model(new_model):
    model=new_model
    print("Model Changed!")

movie_path = '../datasets/movie.csv'
rating_path = '../datasets/rating.csv'
credit_path = '../datasets/credits.csv'
movie_dt = pd.read_csv(movie_path)
rating_dt = pd.read_csv(rating_path)
credit_dt = pd.read_csv(credit_path)

#rating_dt['tmdbId'] = rating_dt['tmdbId'].astype('int')
movie_dt['id'] = movie_dt['id'].astype(int)
rating_dt['tmdbId'] = rating_dt['tmdbId'].astype(int)
rating_dt = rating_dt.dropna(subset=['tmdbId'])
rating_dt.drop(['Unnamed: 0.1', 'Unnamed: 0'], axis=1)

#필요한 컬럼만 선택
selected_columns = ['genres', 'id', 'original_language', 'popularity', 'release_date', 
                    'status', 'title', 'vote_average','production_companies','revenue','poster_path']
movie_dt= movie_dt[selected_columns]

#status가 released가 아닌 영화들 제외
movie_dt = movie_dt[movie_dt['status'] == 'Released'].dropna(subset=['status'])

#popularity 데이터타입 변환
movie_dt['popularity'] = movie_dt['popularity'].astype(float)

def extract_genre_names(genres_string):
    try:
        # 문자열일 때만 처리
        if isinstance(genres_string, str):
            genres_list = ast.literal_eval(genres_string)  # 문자열을 파이썬 객체로 변환
            genre_names = [genre['name'] for genre in genres_list]  # 이름만 추출
            return ', '.join(genre_names)
        else:
            return None  # 문자열이 아닌 경우 None 반환
    except (ValueError, SyntaxError):
        return None  # 변환에 실패하면 None 반환

# 'genres' 컬럼에 적용하여 'name' 리스트만 저장

def extract_actor_names(cast_str):
    cast_list = ast.literal_eval(cast_str)
    actor_names = [cast_member['name'] for cast_member in cast_list]
    return ', '.join(actor_names)


def extract_director_names(crew_str):
    crew_list = ast.literal_eval(crew_str)
    director_names = [crew_member['name'] for crew_member in crew_list if crew_member['job'] == 'Director']
    return ', '.join(director_names)


movie_dt['genres'] = movie_dt['genres'].apply(extract_genre_names)
credit_dt['actor_names'] = credit_dt['cast'].apply(extract_actor_names)
credit_dt['director_names'] = credit_dt['crew'].apply(extract_director_names)

#데이터 변환
movie_dt['id'] = movie_dt['id'].astype(str)
credit_dt['id'] = credit_dt['id'].astype(str)

movie_dt = pd.merge(movie_dt, credit_dt[['id', 'actor_names', 'director_names']], on='id', how='left')
movie_dt.head(2)

# 개봉연도 열 추가
movie_dt['release_year'] = pd.to_datetime(movie_dt['release_date']).dt.year
movie_dt['release_year'] = movie_dt['release_year'].fillna(0).astype(int)
print(movie_dt[['title', 'release_year']].head())

rating_dt['tmdbId'] = rating_dt['tmdbId'].fillna(0).astype(int)
movie_dt['id'] = movie_dt['id'].astype('int32')
movie_dt['release_year'] = pd.to_datetime(movie_dt['release_year'], errors='coerce').dt.year
movie_dt['release_year'] = movie_dt['release_year'].fillna(0).astype(int)

# 사용자 프로필 생성
def build_user_profile(user_id, rating_dt, movie_dt):
    # 사용자가 평점을 준 영화 정보 가져오기
    user_ratings = rating_dt[rating_dt['userId'] == user_id]
    print(f'UNIQUE:{user_ratings["tmdbId"].unique()}, type:{user_ratings["tmdbId"].dtype}')
    print(movie_dt['id'].dtype)
    # 'tmdbId'와 'id'를 매핑하여 사용자의 영화 정보를 가져오기
    user_movies = movie_dt[movie_dt['id'].isin(user_ratings['tmdbId'].astype(int))].copy()
    print(f"UserMovies1:{user_movies}")
    user_movies.reset_index(drop=True, inplace=True)  # 인덱스 재설정
    print(f"UserMovies2:{user_movies}")

    # 영화 장르, 배우, 감독 데이터 하나의 텍스트로 합치기
    user_movies['combined_features'] = (
        user_movies['genres'].fillna('') + ' ' +
        user_movies['actor_names'].fillna('') + ' ' +
        user_movies['director_names'].fillna('')
    )
    
    # TF-IDF -> 영화 특징 벡터화
    tfidf = TfidfVectorizer(token_pattern=r'[^| ]+')  # '|' 또는 공백으로 구분된 특징들
    tfidf_matrix = tfidf.fit_transform(user_movies['combined_features'])

    # 평점 가중치 반영
    weighted_tfidf = np.zeros(tfidf_matrix.shape)
    for idx, row in user_ratings.iterrows():
        # 'id'와 'tmdbId'가 일치하는 인덱스 찾기
        movie_index = user_movies.index[user_movies['id'].astype(int) == int(row['tmdbId'])].tolist()

        # 디버깅용 출력
        #print(f"Matching tmdbId {row['tmdbId']} with movie_index: {movie_index}, tfidf_matrix shape: {tfidf_matrix.shape}")
        
        # movie_index가 존재하고, tfidf_matrix의 범위 내인지 확인
        if movie_index and movie_index[0] < tfidf_matrix.shape[0]:
            # tfidf_matrix와 weighted_tfidf 인덱스 확인
            #print(f"Applying weight for movie_index: {movie_index[0]}")
            weighted_tfidf[movie_index[0], :] = tfidf_matrix[movie_index[0], :].toarray() * float(row['rating'])
        else:
            print(f"Movie with tmdbId {row['tmdbId']} not found or index out of range.")

    # 사용자 프로필 벡터 생성
    user_profile = np.mean(weighted_tfidf, axis=0)

    return user_profile, tfidf


# 사용자 프로필과 영화 유사도 비교, 개봉연도 가중치 추가
def content_based_recommendation(user_id, movie_dt, rating_dt, num_recommendations, bonus_weight):
    # 사용자 프로필 생성
    print(f'RATING DT:{rating_dt}')
    user_profile, tfidf = build_user_profile(user_id, rating_dt, movie_dt)
    

    # 영화 특징 추출 및 TF-IDF 변환
    movie_dt['combined_features'] = (
        movie_dt['genres'].fillna('') + ' ' + 
        movie_dt['actor_names'].fillna('') + ' ' + 
        movie_dt['director_names'].fillna('')
    )
    tfidf_matrix = tfidf.transform(movie_dt['combined_features'])

    # 사용자 프로필과 영화 간 코사인 유사도 계산
    cosine_sim = cosine_similarity(user_profile.reshape(1, -1), tfidf_matrix).flatten()

    # 사용자가 평가한 영화들의 개봉연도 가져오기
    user_rated_movies = rating_dt[rating_dt['userId'] == user_id]['tmdbId'].values
    rated_movie_years = movie_dt[movie_dt['id'].isin(user_rated_movies)]['release_year'].values

    # 영화 코사인 유사도 계산 + 개봉연도 가중치 부여
    movie_scores_with_bonus = []
    similarity_scores=[]
    for idx, predicted_rating in enumerate(cosine_sim):
        if idx < len(movie_dt):
            movie_id = movie_dt.iloc[idx]['id']
            movie_year = movie_dt.iloc[idx]['release_year']

            # 개봉연도 가중치 계산
            if len(rated_movie_years) > 0:
                date_diff = np.mean([abs(movie_year - rated_year) for rated_year in rated_movie_years])
                proximity_bonus = 1 / (1 + date_diff)
            else:
                proximity_bonus = 0

            # 최종 점수 계산
            total_score = predicted_rating + bonus_weight * proximity_bonus
            movie_scores_with_bonus.append((movie_id, total_score))

    
     # 최종 점수 기준으로 상위 10개의 영화 출력
    top_10_movies = sorted(movie_scores_with_bonus, key=lambda x: x[1], reverse=True)[:10]  # 상위 10개 점수
    
    result_movie_ids = []
    result_total_scores = []
    print("상위 10개 최종점수를 가진 영화:")
    for movie_id, total_score in top_10_movies:
        movie_title = movie_dt[movie_dt['id'] == movie_id]['title'].values[0]
        print(f"영화 ID {movie_id} ({movie_title}): 최종점수 {total_score}")
        result_movie_ids.append(movie_id)
        result_total_scores.append(total_score)
    
    
        
    # 영화 추천 결과 정렬 후 상위 추천 영화 선택
    top_recommendations = sorted(movie_scores_with_bonus, key=lambda x: x[1], reverse=True)[:num_recommendations]
    top_movie_ids = [rec[0] for rec in top_recommendations]
    recommended_movies = movie_dt[movie_dt['id'].isin(top_movie_ids)]['title']
    recommended_ratings = [rec[1] for rec in top_recommendations]
    print(f'TYPE2::{type(result_movie_ids)}, {type(result_total_scores)}')

    result_movie_ids = np.array(result_movie_ids)
    result_total_scores = np.array(result_total_scores)
    return result_movie_ids.tolist(), result_total_scores.tolist()



is_first_login = True
first_list_movies = []
first_list_ratings = []
# CSR 형식으로 변환
user_item_matrix = csr_matrix((rating_dt['rating'], (rating_dt['userId'], rating_dt['tmdbId'])))


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
    print(result_list)
    global first_list_movies
    first_list_movies = result_list['id'].astype(str).to_list()
    return first_list_movies



def set_first_ratings(movie_id, ratings):
    new_user_ratings = {    
        'userId': int(current_user_id),
        'tmdbId': movie_id,
        'rating': ratings  # 유저가 입력한 평점
    }

    # DataFrame으로 변환
    global new_ratings_df
    new_ratings_df = pd.DataFrame({'userId': [int(current_user_id)] * len(movie_id), 'tmdbId': movie_id, 'rating':ratings})
    existing_movie_ids = user_item_matrix.shape[1]
    # 신규 유저 평점 벡터 생성
    global new_user_vector
    new_user_vector = np.zeros(existing_movie_ids)
    # 신규 유저의 평점을 벡터에 채워넣기
    for _, row in new_ratings_df.iterrows():
        movie_index = int(row['tmdbId'])  # 영화 ID
        new_user_vector[movie_index] = row['rating']  # 평점 입력

    ## 새로운 유저 벡터를 2차원 형태로 변환 (1 x 영화 개수)
    #new_user_vector_2d = np.reshape(new_user_vector, (1, -1))
    ### csr_matrix로 변환
    #new_user_csr = csr_matrix(new_user_vector_2d)
    ### 기존 행렬에 새로운 유저 벡터 추가
    #user_item_matrix = vstack([user_item_matrix, new_user_csr])

def get_recommend(type=1, num_recommend=10):
    print(f"RECOMMEND TYPE:{type}, ID:{int(current_user_id)}")
    if type == 1:
        if 'new_user_vector' in globals():
            rec_movies, rec_ratings = recommend_movie_by_als(int(current_user_id), new_user_vector=new_user_vector)
        else:
            rec_movies, rec_ratings = recommend_movie_by_als(int(current_user_id))
        return rec_movies, rec_ratings
    elif type == 2:
        if 'new_ratings_df' in globals() and not new_ratings_df.empty:
            rec_movies_cont, rec_ratings_cont = recommend_movie_by_contentbased(int(current_user_id), rate_dataframe = new_ratings_df, n_movies=10)
        else:
            rec_movies_cont, rec_ratings_cont = recommend_movie_by_contentbased(int(current_user_id))
        return rec_movies_cont, rec_ratings_cont



def recommend_movie_by_contentbased(userId, rate_dataframe=rating_dt, n_movies=10):
    rec_movies, rec_ratings = content_based_recommendation(user_id=userId,movie_dt=movie_dt, rating_dt=rate_dataframe, num_recommendations=10,bonus_weight=0.1)
    return rec_movies, rec_ratings


#유저 아이디를 입력하면 다섯개의 추천 목록을 뽑아준다.
#def recommend_movie_by_als(user_id, n_movies=10):
#    print(f'User id: {user_id}, n_movies={n_movies}')
#    print(type(user_id))
#    print(type(n_movies))
#    if user_id > rating_dt['userId'].max():
#        recommendations = model.recommend(0, csr_matrix(new_user_vector), N=n_movies)
#    else:
#        recommendations = model.recommend(user_id, user_item_matrix[user_id], N=n_movies)
#    movie_arr = []
#    rating_arr = []
#    for idx in recommendations[0]:
#        movie_arr.append(str(idx))
#
#    for idx in recommendations[1]:
#        rating_arr.append(str(idx))
#
#    return movie_arr,rating_arr
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


def recommend_movie_by_als(user_id, n_movies=10, new_user_vector=None):
    # 사용자가 이미 평가한 영화와 평점 출력
    user_ratings = rating_dt[rating_dt['userId'] == user_id]
    print(f"User {user_id}의 평가 영화 및 평점:")
    for idx, row in user_ratings.iterrows():
        movie_title = movie_dt.loc[movie_dt['id'] == int(row['tmdbId']), 'title'].values
        if len(movie_title) > 0:
            print(f"- {movie_title[0]}: {row['rating']}점")
        else:
            print(f"- tmdbId {row['tmdbId']}에 해당하는 영화 제목을 찾을 수 없습니다.")
    
    # ALS 모델을 사용하여 추천 영화 목록 생성
    print(f"\nUser {user_id}에게 추천하는 영화 {n_movies}개:")
    if 'new_user_vector' in globals():
        print("신규유저..")
        # new_user_vector를 CSR 형식으로 변환
        new_user_vector_csr = csr_matrix(new_user_vector)

        # 변환된 CSR 형식을 사용하여 추천 생성, recalculate_user=True 사용
        recommendations = model.recommend(
            userid=user_id,
            user_items=new_user_vector_csr,
            N=n_movies,
            recalculate_user=True
        )
    else:
        print("기존유저...왜안될까..")
        existing_movie_ids = user_item_matrix.shape[1]
        user_vector = np.zeros(existing_movie_ids)
            # 신규 유저의 평점을 벡터에 채워넣기
        for _, row in user_ratings.iterrows():
            movie_index = int(row['tmdbId'])  # 영화 ID
            user_vector[movie_index] = row['rating']  # 평점 입력

        user_vector_csr = csr_matrix(user_vector)

        # 변환된 CSR 형식을 사용하여 추천 생성, recalculate_user=True 사용
        recommendations = model.recommend(
            userid=user_id,
            user_items=user_vector_csr,
            N=n_movies,
            recalculate_user=True
        )
        #recommendations = model.recommend(user_id, user_vector_csr, N=n_movies)
        

    # 추천된 영화 ID 목록 추출
    recommended_ids = recommendations[0]

    # 추천된 ID가 movie_dt에 있는지 확인 및 필터링
    valid_recommended_ids = [ids for ids in recommended_ids if ids in movie_dt['id'].values]
    missing_ids = [ids for ids in recommended_ids if ids not in movie_dt['id'].values]

    if missing_ids:
        print(f"movie_dt에서 찾을 수 없는 추천된 ID: {missing_ids}")
    else:
        print("모든 추천된 ID가 movie_dt에 있습니다.")

    # 추천된 영화 목록 출력
    for ids in valid_recommended_ids:
        movie_title = movie_dt.loc[movie_dt['id'] == ids, 'title'].values
        if len(movie_title) > 0:
            print(f"- {movie_title[0]}")
        else:
            print(f"- 추천된 id {ids}에 해당하는 영화 제목을 찾을 수 없습니다.")

    print(f"REC01:{recommendations[0]}")
    print(f"REC01:{recommendations[1]}")
    print(f'TYPE2::{type(recommendations[0])}, {type(recommendations[1])}')
    print(f'TYPE2::{type(recommendations[0].tolist())}, {type(recommendations[1].tolist())}')

    return recommendations[0].tolist(),recommendations[1].tolist()
