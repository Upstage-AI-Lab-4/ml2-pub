import requests
import os
import csv
import json
import pandas as pd

def append_data_to_dataset(df, data):
    df.loc[len(df)] = data
    return df

file_path = '../datasets/movie_detail_data.csv'

# 파일이 존재하는지 확인
if not os.path.exists(file_path):
    # 파일이 없으면 새로 생성
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['adult','belongs_to_collection','budget','genres','homepage','id','imdb_id','original_language','original_title','overview','popularity','poster_path','production_companies','production_countries','release_date','revenue','runtime','spoken_languages','status','tagline','title','video','vote_average','vote_count'])

movie_df = pd.read_csv(file_path)

year_range = range(2020, 2025)
month_range = range(1, 13)

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiMmY1N2RmMjUzZjIyZTAwMTQ5MjRjYjdhYmI1MWIxOSIsIm5iZiI6MTcyODE4NDI5Mi44MjE4MjksInN1YiI6IjY3MDFmZTM4Zjg3OGFkZmVkMDg1ODRlMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.6IP5mBurL06yy5lF0FOGAoCxnxmDW6oF9p6Xp7utISM"
}
movie_array = []
for year in year_range:
    for month in month_range:
        if month == 12:
            month_add = 1
            year_add = year+1
        else:
            month_add = month+1
            year_add = year
        
        print(f'Currently Parsing in year: {year}, month:{month}, Cunrrent count: {len(movie_array)}')

        page = 1
        while True:
            url = f"https://api.themoviedb.org/3/discover/movie?page={page}&primary_release_date.gte={year}-{month}-02&primary_release_date.lte={year_add}-{month_add}-01&sort_by=popularity.desc"
            response_data = requests.get(url, headers=headers).json()
                #result가 더이상 없으면 while문 빠져나가야
            if len(response_data['results'])<1:
                break
            
            for item in response_data['results']:
                url_detail = f"https://api.themoviedb.org/3/movie/{item['id']}"
                json_item = requests.get(url_detail, headers=headers).json()
                movie_array.append(json_item)
            page = page+1

movie_df = pd.DataFrame(movie_array)
movie_df.to_csv(file_path)