import ast

def handler(movie_dt):
    print('preprocess')
    #결측치가 32000개 이상인건 의미없다고 판단 (영화가 4만 5천개인데 3만5천개면 )75% 결측)
    drop_column_list = list(movie_dt.columns[movie_dt.isnull().sum()<=35000])
    movie_dt = movie_dt[drop_column_list]

    #status가 released가 아닌 영화들은 볼수 없으니 제외
    #데이터셋이 과거의 자료여서 post production, In Production 등 production중인 영화들은 이미 개봉했을 수 있지만
    #무비 데이터를 최신으로 변경하기 전까지는 현재 데이터셋에선 우선 제거하는걸로
    movie_dt = movie_dt[movie_dt['status'] == 'Released'].dropna(subset=['status'])

    #지금단계에서 필요없어보이는 column 제거
    movie_dt = movie_dt.drop(['overview', 'poster_path', 'tagline', 'spoken_languages'], axis=1)    

    return movie_dt
