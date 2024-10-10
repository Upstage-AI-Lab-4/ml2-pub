import pandas as pd
import numpy as np
import pickle
import warnings;warnings.filterwarnings('ignore')

from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import TruncatedSVD
from torch.utils.data import DataLoader, TensorDataset
from torch.cuda.amp import autocast, GradScaler

# 필요한 데이터 load
movie_path = '../datasets/movie.csv'
rating_path = '../datasets/rating.csv'
credit_path = '../datasets/credit.csv'
movie_dt = pd.read_csv(movie_path)
rating_dt = pd.read_csv(rating_path)
credit_dt = pd.read_csv(credit_path)

rating_dt.drop(['Unnamed: 0.1', 'Unnamed: 0'], axis=1)

#필요한 컬럼만 선택
selected_columns = ['genres', 'id', 'original_language', 'popularity', 'release_date', 
                    'status', 'title', 'vote_average','production_companies']
movie_dt= movie_dt[selected_columns]

#status가 released가 아닌 영화들 제외
movie_dt = movie_dt[movie_dt['status'] == 'Released'].dropna(subset=['status'])

#popularity 데이터타입 변환
movie_dt['popularity'] = movie_dt['popularity'].astype(float)

# genres 컬럼의 데이터 타입 및 일부 샘플 확인
print(movie_dt['genres'].dtype)
print(movie_dt['genres'].head(10))


#장르 추출
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
movie_dt['genres'] = movie_dt['genres'].apply(extract_genre_names)

# 결과 확인
print(movie_dt['genres'].head())

#배우 추출
def extract_actor_names(cast_str):
    cast_list = ast.literal_eval(cast_str)
    actor_names = [cast_member['name'] for cast_member in cast_list]
    return ', '.join(actor_names)

credit_dt['actor_names'] = credit_dt['cast'].apply(extract_actor_names)

print(credit_dt[['actor_names']].head())

#감독 추출
def extract_director_names(crew_str):
    crew_list = ast.literal_eval(crew_str)
    director_names = [crew_member['name'] for crew_member in crew_list if crew_member['job'] == 'Director']
    return ', '.join(director_names)

credit_dt['director_names'] = credit_dt['crew'].apply(extract_director_names)

print(credit_dt[['director_names']].head())


#데이터 변환
movie_dt['id'] = movie_dt['id'].astype(str)
credit_dt['id'] = credit_dt['id'].astype(str)

movie_dt = pd.merge(movie_dt, credit_dt[['id', 'actor_names', 'director_names']], on='id', how='left')
movie_dt.head(2)

# 개봉연도 열 추가
movie_dt['release_year'] = pd.to_datetime(movie_dt['release_date']).dt.year
movie_dt['release_year'] = movie_dt['release_year'].fillna(0).astype(int)
print(movie_dt[['title', 'release_year']].head())

rating_dt['tmdbId'] = rating_dt['tmdbId'].fillna(0).astype('int32')
movie_dt['id'] = movie_dt['id'].astype('int32')
movie_dt['release_year'] = pd.to_datetime(movie_dt['release_year'], errors='coerce').dt.year
movie_dt['release_year'] = movie_dt['release_year'].fillna(0).astype(int)

# 사용자 프로필 생성
def build_user_profile(user_id, rating_dt, movie_dt):
    # 사용자가 평점을 준 영화 정보 가져오기
    user_ratings = rating_dt[rating_dt['userId'] == user_id]
    
    # 'tmdbId'와 'id'를 매핑하여 사용자의 영화 정보를 가져오기
    user_movies = movie_dt[movie_dt['id'].isin(user_ratings['tmdbId'].values)].copy()
    user_movies.reset_index(drop=True, inplace=True)  # 인덱스 재설정

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
        movie_index = user_movies.index[user_movies['id'] == row['tmdbId']].tolist()

        # 디버깅용 출력
        #print(f"Matching tmdbId {row['tmdbId']} with movie_index: {movie_index}, tfidf_matrix shape: {tfidf_matrix.shape}")
        
        # movie_index가 존재하고, tfidf_matrix의 범위 내인지 확인
        if movie_index and movie_index[0] < tfidf_matrix.shape[0]:
            # tfidf_matrix와 weighted_tfidf 인덱스 확인
            #print(f"Applying weight for movie_index: {movie_index[0]}")
            weighted_tfidf[movie_index[0], :] = tfidf_matrix[movie_index[0], :].toarray() * row['rating']
        else:
            print(f"Movie with tmdbId {row['tmdbId']} not found or index out of range.")

    # 사용자 프로필 벡터 생성
    user_profile = np.mean(weighted_tfidf, axis=0)

    return user_profile, tfidf


# 사용자 프로필과 영화 유사도 비교, 개봉연도 가중치 추가
def content_based_recommendation(user_id, movie_dt, rating_dt, num_recommendations, bonus_weight):
    # 사용자 프로필 생성
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
    
    print("상위 10개 최종점수를 가진 영화:")
    for movie_id, total_score in top_10_movies:
        movie_title = movie_dt[movie_dt['id'] == movie_id]['title'].values[0]
        print(f"영화 ID {movie_id} ({movie_title}): 최종점수 {total_score}")
        
    # 영화 추천 결과 정렬 후 상위 추천 영화 선택
    top_recommendations = sorted(movie_scores_with_bonus, key=lambda x: x[1], reverse=True)[:num_recommendations]
    top_movie_ids = [rec[0] for rec in top_recommendations]
    recommended_movies = movie_dt[movie_dt['id'].isin(top_movie_ids)]['title']
    recommended_ratings = [rec[1] for rec in top_recommendations]

    return recommended_movies, recommended_ratings


user_id = 50
num_recommendations = 5
bonus_weight=0.1
recommended_movies, recommended_ratings = content_based_recommendation(user_id, movie_dt, rating_dt, num_recommendations, bonus_weight)

print(f"User {user_id}에게 추천된 영화:\n", recommended_movies, recommended_ratings)