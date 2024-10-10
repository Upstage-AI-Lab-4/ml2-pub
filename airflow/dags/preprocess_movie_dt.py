import ast

def handler(movie_dt):
    print('preprocess')
    drop_column_list = list(movie_dt.columns[movie_dt.isnull().sum()<=35000])
    movie_dt = movie_dt[drop_column_list]
    movie_dt = movie_dt[movie_dt['status'] == 'Released'].dropna(subset=['status'])
    movie_dt = movie_dt.drop(['overview', 'poster_path', 'tagline', 'status', 'spoken_languages'], axis=1)
    movie_dt['popularity'] = movie_dt['popularity'].astype(float)
    
    def extract_genre_names(genres_string):
        genres_list = ast.literal_eval(genres_string)  # 문자열을 파이썬 객체로 변환
        genre_names = [genre['name'] for genre in genres_list]  # 이름만 추출
        return ', '.join(genre_names)  # 쉼표로 연결

    movie_dt['genre_names'] = movie_dt['genres'].apply(extract_genre_names)

    return movie_dt
