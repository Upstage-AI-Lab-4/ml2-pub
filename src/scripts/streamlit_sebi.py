import streamlit as st
import pandas as pd
import ast
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix

# 데이터 로드
def load_data(movie_path, rating_path):
    movie_dt = pd.read_csv(movie_path, low_memory=False)
    rating_dt = pd.read_csv(rating_path, low_memory=False)

    # 결측치 처리
    drop_column_list = list(movie_dt.columns[movie_dt.isnull().sum() <= 35000])
    movie_dt = movie_dt[drop_column_list]
    movie_dt = movie_dt[movie_dt['status'] == 'Released'].dropna(subset=['status'])
    movie_dt = movie_dt.drop(['overview', 'poster_path', 'tagline', 'status', 'spoken_languages'], axis=1)
  
    # 장르 추출
    movie_dt['genre_names'] = movie_dt['genres'].apply(extract_genre_names)

    return movie_dt, rating_dt

# 장르 추출 함수
def extract_genre_names(genres_string):
    try:
        genres_list = ast.literal_eval(genres_string)
        genre_names = [genre['name'] for genre in genres_list]
        return ', '.join(genre_names)
    except (ValueError, SyntaxError, TypeError):
        return ''

# 유저 판별 함수
def check_user(user_id, rating_dt):
    if user_id in rating_dt['userId'].unique():
        return "existing"
    else:
        return "new"

# 신규 유저 ID 생성 함수
def make_new_user_id(rating_dt):
    return rating_dt['userId'].max() + 1

# ALS 모델 학습 함수
def train_als_model(rating_dt):
    rating_dt['userId'] = rating_dt['userId'].astype(int)
    rating_dt['movieId'] = rating_dt['movieId'].astype(int)

    # CSR 형식으로 변환
    user_item_matrix = csr_matrix((rating_dt['rating'], (rating_dt['userId'], rating_dt['movieId'])))

    # ALS 모델 초기화 및 학습
    model = AlternatingLeastSquares(factors=10, regularization=0.1, iterations=20)
    model.fit(user_item_matrix)

    return model, user_item_matrix

# 영화 추천 함수
def recommend_movie_by_als(user_id, model, user_item_matrix, movie_dt, n_movies=5):
    recommendations = model.recommend(user_id, user_item_matrix[user_id], N=n_movies)
    recommended_movies = []
    for ids in recommendations[0]:
        movie_title = movie_dt.loc[movie_dt.index == ids, 'title'].values
        recommended_movies.append(movie_title[0])
    return recommended_movies

# 장르 선택 함수
def select_genres(movie_dt):
    unique_genres = movie_dt['genre_names'].dropna().str.split(', ').explode().unique()
    unique_genres = [genre for genre in unique_genres if genre != '']  # 빈 문자열을 제외
    
    # 장르 선택
    selected_genres = st.multiselect(
        "좋아하는 장르를 선택하세요 (최대 5개):", 
        unique_genres,  
        default=st.session_state.get('selected_genres', []),
        max_selections=5
    )
    st.session_state.selected_genres = selected_genres

    # '선택' 버튼 추가
    if st.button("선택"):
        if len(selected_genres) > 0:
            filtered_movies = movie_dt[movie_dt['genre_names'].apply(lambda x: any(genre in x for genre in selected_genres))]
            st.session_state.top_movies_by_revenue = filtered_movies.nlargest(20, 'revenue')
            st.session_state.genres_selected = True  # 장르 선택 완료 상태로 설정
        else:
            st.warning("최소 1개의 장르를 선택하세요.")  # 경고 메시지

# 평점 데이터 저장 함수
def save_ratings_to_csv(updated_ratings, rating_path):
    updated_ratings.to_csv(rating_path, index=False)

# 영화 평가 및 평점 부여
def rate_movies(movie_dt, user_id, rating_dt, rating_path):
    if 'top_movies_by_revenue' in st.session_state:
        top_movies = st.session_state.top_movies_by_revenue[['title', 'id']]

        # 영화 평가 상태를 저장할 session_state 초기화
        if 'movie_ratings' not in st.session_state:
            st.session_state.movie_ratings = {}

        st.write("영화 평가를 입력해주세요:")

        # 두 개의 영화를 가로로 배치하는 로직
        for i in range(0, len(top_movies), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(top_movies):
                    movie = top_movies.iloc[i + j]
                    with cols[j]:
                        # 영화 제목 위 구분선 추가
                        st.markdown("<hr style='border: 1px solid #ddd;'>", unsafe_allow_html=True)

                        # 영화 제목 출력
                        st.write(f"**{movie['title']}**")

                        # 영화 평가 상태 업데이트 (라디오 버튼은 HTML과 분리)
                        rating = st.radio(
                            '평가를 선택하세요:',
                            ('재밌게 봤어요', '재미 없었어요', '안 봤어요'),
                            key=f"rating_{movie['id']}"
                        )

                        if rating == '재밌게 봤어요':
                            st.session_state.movie_ratings[movie['id']] = 4.0
                        elif rating == '재미 없었어요':
                            st.session_state.movie_ratings[movie['id']] = 2.0
                        else:
                            st.session_state.movie_ratings[movie['id']] = None

        # 평점 데이터 업데이트
        ratings_list = []
        for movie_id, rating in st.session_state.movie_ratings.items():
            if rating is not None:  # '안 봤어요'가 아닌 경우에만 추가
                ratings_list.append({'userId': user_id, 'movieId': movie_id, 'rating': rating})

        if ratings_list:
            new_ratings = pd.DataFrame(ratings_list)
            updated_ratings = pd.concat([rating_dt, new_ratings], ignore_index=True)
            
            # 업데이트된 데이터를 파일에 저장
            save_ratings_to_csv(updated_ratings, rating_path)  # CSV 파일에 저장
            
            return updated_ratings
    return rating_dt



# 추천 시스템 함수 (ALS 모델을 사용)
def recommend_movies_als(rating_dt, movie_dt, user_id):
    # ALS 모델 학습
    model, user_item_matrix = train_als_model(rating_dt)

    # 영화 추천
    recommended_movies = recommend_movie_by_als(user_id, model, user_item_matrix, movie_dt)

    st.write("추천 영화 목록:")
    for movie in recommended_movies:
        st.write(movie)


# 기존 유저를 위한 즉시 추천 함수
def recommend_for_existing_user(user_id, rating_dt, movie_dt):
    model, user_item_matrix = train_als_model(rating_dt)
    recommended_movies = recommend_movie_by_als(user_id, model, user_item_matrix, movie_dt)
    
    st.write("기존 유저를 위한 추천 영화 목록:")
    for movie in recommended_movies:
        st.write(movie)



# 장르 선택 및 영화 목록 보여주는 함수
def show_movie_list(movie_dt, user_id, rating_dt, rating_path):  # rating_path 추가
    # 장르 선택 및 영화 목록 보기
    select_genres(movie_dt)

    # 평점 입력
    if st.session_state.get('genres_selected', False):
        updated_rating_dt = rate_movies(movie_dt, user_id, rating_dt, rating_path)  # rating_path 추가

        # 최종 확인 버튼 (선택 버튼 이후에만 나타남)
        if st.button('확인'):
            recommend_movies_als(updated_rating_dt, movie_dt, user_id)


# 유저 ID를 부여하는 함수
def get_user_id(user_input, rating_dt):
    if user_input.lower() == 'new':
        user_id = make_new_user_id(rating_dt)
        st.write(f"신규 유저입니다. 부여된 userId는 {user_id}입니다.")
        return user_id, "new"
    else:
        try:
            user_id = int(user_input)
            user_type = check_user(user_id, rating_dt)
            if user_type == "existing":
                st.write(f"기존 유저입니다. userId는 {user_id}입니다.")
                return user_id, "existing"
            else:
                st.write(f"입력한 userId({user_id})는 존재하지 않습니다. 새로 userId를 부여합니다.")
                user_id = make_new_user_id(rating_dt)
                st.write(f"부여된 userId는 {user_id}입니다.")
                return user_id, "new"
        except ValueError:
            st.write("잘못된 userId입니다. 숫자를 입력하세요.")
            user_id = None
    return user_id




# Streamlit UI 메인 함수
def main():
    st.title("영화 추천 시스템")

    # 데이터 로드
    movie_dt, rating_dt = load_data(movie_path, rating_path)

    # 유저 ID 입력
    user_input = st.text_input("본인의 userId를 입력하세요 (신규 유저일 경우 'new'를 입력하세요):")

    if user_input:
        # 유저 ID 부여
        user_id, user_type = get_user_id(user_input, rating_dt)

        if user_id:
            if user_type == "existing":
                # 기존 유저는 바로 추천을 보여줌
                recommend_for_existing_user(user_id, rating_dt, movie_dt)
            else:
                # 신규 유저는 장르 선택 및 영화 목록 보기
                show_movie_list(movie_dt, user_id, rating_dt, rating_path)  # rating_path 추가


# 실행
if __name__ == '__main__':
    movie_path = '../src/datasets/movies_metadata.csv'
    rating_path = '../src/datasets/ratings_small.csv'
    main()
