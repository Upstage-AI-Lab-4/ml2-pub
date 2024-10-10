import streamlit as st
import pandas as pd
import requests
import ast
from datetime import datetime
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix
from fuzzywuzzy import process
# pip install fuzzywuzzy[speedup]

# 데이터 로드
def load_data(movie_path, rating_path):
    movie_dt = pd.read_csv(movie_path, low_memory=False)
    rating_dt = pd.read_csv(rating_path, low_memory=False)

    # 결측치 처리
    drop_column_list = list(movie_dt.columns[movie_dt.isnull().sum() <= 35000])
    movie_dt = movie_dt[drop_column_list]
    movie_dt = movie_dt[movie_dt['status'] == 'Released'].dropna(subset=['status'])
    movie_dt = movie_dt.drop(['poster_path', 'tagline', 'status', 'spoken_languages'], axis=1)
  
    # 장르 추출
    movie_dt['genre_names'] = movie_dt['genres'].apply(extract_genre_names)

    # 날짜 데이터 타입으로 변환
    movie_dt['release_date'] = pd.to_datetime(movie_dt['release_date'], errors='coerce')

    # 결측치 처리 및 최신 영화 필터링 (최신 순, 수익 순, 평점 순)
    movie_dt = movie_dt.dropna(subset=['release_date', 'revenue', 'vote_average'])


    return movie_dt, rating_dt

# OMDb API 키 설정 
OMDB_API_KEY = 'abe9c5cd'

# IMDb ID로 OMDb API에서 영화 포스터 가져오기
def get_movie_poster_by_imdb_id(imdb_id):
    url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data['Response'] == 'True':
        return data['Poster']  # 포스터 URL 반환
    else:
        return None

# 랜덤으로 평점 7점 이상인 영화 추천 함수 (10개의 영화 추천)
def show_random_top_movies(movie_dt, n_recommendations=10):
    st.subheader("🎬 최신 인기 영화")

    # 평점이 7점 이상인 영화 필터링
    top_rated_movies = movie_dt[(movie_dt['vote_average'] >= 7) & (movie_dt['revenue'] > 0)]

    # 수익 상위 80% 기준으로 필터링 (평점 7점 이상 중에서)
    revenue_threshold = top_rated_movies['revenue'].quantile(0.8)
    high_revenue_top_rated_movies = top_rated_movies[top_rated_movies['revenue'] >= revenue_threshold]

    # 최근 8년 내 영화 필터링 (2017년 데이터가 가장 최신)
    recent_movies = high_revenue_top_rated_movies[high_revenue_top_rated_movies['release_date'] >= pd.Timestamp(datetime.now().year - 8, 1, 1)]

    # 영화가 충분히 있으면 랜덤으로 n개의 영화 선택
    if len(recent_movies) >= n_recommendations:
        random_movies = recent_movies.sample(n=n_recommendations)
    else:
        random_movies = recent_movies


    # 랜덤 영화 목록 출력
    for _, movie in random_movies.iterrows():
        # 두 개의 열 생성
        col1, col2 = st.columns([1, 3])  # 비율을 조정해 원하는 레이아웃으로 설정

        # IMDb ID로 포스터 가져오기
        poster_url = get_movie_poster_by_imdb_id(movie['imdb_id'])

        with col1:
            # 포스터 출력 (포스터가 있을 때만)
            if poster_url:
                st.image(poster_url, caption=movie['title'], use_column_width=True)
            else:
                st.write("포스터를 찾을 수 없습니다.")
        
        with col2:
            # 영화 정보 출력
            st.write(f"**{movie['title']}** (개봉일: {movie['release_date'].date()}, 평점: {movie['vote_average']})")
            st.write(f"수익: ${movie['revenue']:,.0f}")
            
            # 영화 개요 (overview)를 expander로 출력
            if isinstance(movie['overview'], str) and pd.notna(movie['overview']):
                with st.expander("overview"):
                    st.write(movie['overview'])
            else:
                st.write("개요: 정보가 없습니다.")
            
        # 영화 간 구분선 추가
        st.write("---")


# 영화 검색 결과를 출력하는 함수 (fuzzy matching 사용, 수익 순 정렬)
def show_search_results(movie_dt, search_query):
    # 영화 제목에서 검색어와 유사한 상위 5개 결과 가져오기
    titles = movie_dt['title'].tolist()
    matching_titles = process.extract(search_query, titles, limit=5)

    # 중복된 제목 제거 (set 사용)
    unique_titles = list(set([title for title, score in matching_titles]))

    if not unique_titles:
        st.write("검색 결과가 없습니다.")
    else:
        # 영화 정보를 리스트로 수집
        movies = []
        for title in unique_titles:
            movie = movie_dt[movie_dt['title'] == title].iloc[0]
            movies.append(movie)

        # 수익 순으로 정렬
        sorted_movies = sorted(movies, key=lambda x: x['revenue'], reverse=True)

        # 검색 결과 출력 (수익 순)
        for movie in sorted_movies:
            # 두 개의 열 생성
            col1, col2 = st.columns([1, 3])  # 비율을 조정해 원하는 레이아웃으로 설정

            # IMDb ID로 포스터 가져오기
            poster_url = get_movie_poster_by_imdb_id(movie['imdb_id'])

            with col1:
                # 포스터 출력 (포스터가 있을 때만)
                if poster_url:
                    st.image(poster_url, caption=movie['title'], use_column_width=True)
                else:
                    st.write("포스터를 찾을 수 없습니다.")
            
            with col2:
                # 영화 정보 출력
                st.write(f"**{movie['title']}** (개봉일: {movie['release_date'].date()}, 평점: {movie['vote_average']})")
                st.write(f"수익: ${movie['revenue']:,.0f}")
                
                # 영화 개요 (overview)를 expander로 출력
                if isinstance(movie['overview'], str) and pd.notna(movie['overview']):
                    with st.expander("overview"):
                        st.write(movie['overview'])
                else:
                    st.write("개요: 정보가 없습니다.")
                
            # 영화 간 구분선 추가
            st.write("---")

# 홈화면에 기본 추천 시스템 (사용자 정보 없이)
def show_basic_recommendation_home(movie_dt, rating_dt):
    # 랜덤 추천: 평점 7점 이상 영화
    show_random_top_movies(movie_dt)




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
                            ('재미 있었어요', '재미 없었어요', '안 봤어요'),
                            key=f"rating_{movie['id']}"
                        )

                        if rating == '재미 있었어요':
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



# 유저 ID를 사이드바에서 입력받는 함수
def sidebar_user_input(rating_dt):
    st.sidebar.header("유저 ID 입력")
    user_input = st.sidebar.text_input("본인의 userId를 입력하세요 (신규 유저일 경우 'new'를 입력하세요):")

    if user_input:
        user_id, user_type = get_user_id(user_input, rating_dt)
        if user_id:
            st.session_state.user_id = user_id
            return user_id, user_type
    return None, None


# 유저 ID 입력을 사이드바에서 받고 추천 시스템을 진행하는 함수
def user_recommendation_page(user_id, rating_dt, movie_dt):
    st.subheader(f"환영합니다, 유저 {user_id}님!")
    st.write("추천 시스템을 시작합니다.")

    user_type = check_user(user_id, rating_dt)
    if user_type == "existing":
        recommend_for_existing_user(user_id, rating_dt, movie_dt)
    else:
        show_movie_list(movie_dt, user_id, rating_dt, rating_path)


# 유저 ID를 부여하는 함수
def get_user_id(user_input, rating_dt):
    if user_input.lower() == 'new':
        user_id = make_new_user_id(rating_dt)
        st.sidebar.write(f"신규 유저입니다. 부여된 userId는 {user_id}입니다.")
        return user_id, "new"
    else:
        try:
            user_id = int(user_input)
            user_type = check_user(user_id, rating_dt)
            if user_type == "existing":
                st.sidebar.write(f"기존 유저입니다. userId는 {user_id}입니다.")
                return user_id, "existing"
            else:
                st.sidebar.write(f"입력한 userId({user_id})는 존재하지 않습니다. 새로 userId를 부여합니다.")
                user_id = make_new_user_id(rating_dt)
                st.sidebar.write(f"부여된 userId는 {user_id}입니다.")
                return user_id, "new"
        except ValueError:
            st.sidebar.write("잘못된 userId입니다. 숫자를 입력하세요.")
            user_id = None
    return user_id


# Streamlit UI 메인 함수
def main():
    st.set_page_config(page_title="영화 추천 시스템", layout="wide")

    st.title("🎥 영화 추천 시스템")
    st.markdown("영화 평점을 기반으로 개인 맞춤형 영화 추천을 제공합니다.")



    # 데이터 로드
    movie_dt, rating_dt = load_data(movie_path, rating_path)

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["최신 영화 목록", "유저 ID 입력 및 추천 시스템", "영화 검색"])

    with tab1:
        # 최신 인기 영화 목록 출력
        show_basic_recommendation_home(movie_dt, rating_dt)

    with tab2:
        # 사이드바에서 유저 ID 입력 및 추천 시스템 실행
        user_id, user_type = sidebar_user_input(rating_dt)
        if user_id:
            user_recommendation_page(user_id, rating_dt, movie_dt)

    with tab3:
        # 영화 검색 기능
        st.subheader("🎥 영화 검색")
        search_query = st.text_input("영화 제목을 입력하세요:")
        if search_query:
            show_search_results(movie_dt, search_query)



# 실행
if __name__ == '__main__':
    movie_path = '/root/src/datasets/movies_metadata.csv'
    rating_path = '/root/src/datasets/ratings_small.csv'
    main()
