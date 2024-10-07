import requests
import os
import csv
import json
import pandas as pd
from datetime import datetime,timedelta

yesterday = datetime.today() - timedelta(1)
yesterday_string = yesterday.strftime("%Y-%m-%d")
print(f'Update Changed at yesterday {yesterday_string}')
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiMmY1N2RmMjUzZjIyZTAwMTQ5MjRjYjdhYmI1MWIxOSIsIm5iZiI6MTcyODMwNzU4MC44ODg0MDcsInN1YiI6IjY3MDFmZTM4Zjg3OGFkZmVkMDg1ODRlMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.RAV-a8EgeXOQaaZXmpapdxFkpRgwUaVC4mZmlVt8u4U"
}

changed_movie_array = []

page = 1
while True:
    url = f"https://api.themoviedb.org/3/movie/changes?end_date={yesterday_string}&page={page}&start_date={yesterday_string}"
    response_data = requests.get(url, headers=headers).json()
    if len(response_data['results'])<1:
        break
    for item in response_data['results']:
        url_detail = f"https://api.themoviedb.org/3/movie/{item['id']}"
        json_item = requests.get(url_detail, headers=headers).json()
        changed_movie_array.append(json_item)        
    page = page+1

changed_df = pd.DataFrame(changed_movie_array)
print(f'Total Changed Number: {len(changed_df)}')

file_path = '../datasets/movie_detail_data.csv'
movie_df = pd.read_csv(file_path)
movie_df = pd.concat([movie_df, changed_df])

movie_df.to_csv(file_path)
print(f'Update Complete')