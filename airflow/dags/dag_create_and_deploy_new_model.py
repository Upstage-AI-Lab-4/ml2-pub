from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

import warnings; warnings.filterwarnings('ignore')
import pandas as pd
import ast
import asl
import log_to_mlflow
import notify_to_api_server
import get_latest_file

def preprocess(movie_dt):
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

def get_latest_dataset():
    base_path = './datasets'
    movie_path = get_latest_file.handler(base_path, 'movies_metadata')
    rating_path = get_latest_file.handler(base_path, 'ratings_small')

    print(f'load movie data: {movie_path}')
    movie_dt = pd.read_csv(movie_path)
    print(f'load rating data: {rating_path}')
    rating_dt = pd.read_csv(rating_path)

    return (movie_dt, rating_dt)

def create_model():
    (movie_dt, rating_dt) = get_latest_dataset()
    movie_dt = preprocess(movie_dt)
    wrapped_model = asl.handler(movie_dt, rating_dt)
    
# mlflow 설정
    print('configure mlflow')
    # 추가 모델 설정시 아래 변수들에 대한 동적 설정 혹은 dag 분리
    experiment_name = f'ALS_movie_recommendation'
    model_name = 'movie ALS'

    return log_to_mlflow.handler(wrapped_model, experiment_name, model_name)

# Define the DAG
with DAG('create_and_deploy_new_model',
          description='create model and deploy', 
          schedule_interval='0 0 * * *', 
          start_date=datetime(2024, 10, 7), 
          catchup=False) as dag:

    task1 = PythonOperator(task_id='modeling_task',
                        python_callable=create_model,
                        dag=dag)


    task2 = PythonOperator(task_id='notify_to_api_server',
                        python_callable=notify_to_api_server.handler,
                        dag=dag)


task1 >> task2
