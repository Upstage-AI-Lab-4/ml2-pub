from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

import pandas as pd
import numpy as np
import ast
import warnings; warnings.filterwarnings('ignore')
import tag

from sklearn.metrics.pairwise import cosine_similarity 
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix

def handler():
    print('load data')
    movie_path = './datasets/movies_metadata.csv'
    rating_path = './datasets/ratings_small.csv'
    movie_dt = pd.read_csv(movie_path)
    rating_dt = pd.read_csv(rating_path)

    print('preprocess')
    movie_path = '../datasets/movies_metadata.csv'
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

    user_item_matrix = csr_matrix((rating_dt['rating'], (rating_dt['userId'], rating_dt['movieId'])))

    print('create ALS model')
    model = AlternatingLeastSquares(factors=10, regularization=0.1, iterations=20)
    model.fit(user_item_matrix)
    
# mlflow 설정
    print('configure mlflow')
    dataset_name = '2099-12-31'
    experiment_name = f'ALS_{dataset_name}'
    tag.set_experiment(experiment_name)

    print('log to mlflow')
    with tag.run(experiment_name) as run:
        tag.log_model(experiment_name, python_model=tag.ALSWrapper(model))

        print(f'register model, run: {run.info.run_id}')
        model_name = 'movie ALS'
        model_version = tag.model_register(model_name, run.info.run_id)

        print(f'give model a version, model_version: {model_version.version}')
        tag.promote_to_production(model_name, model_version.version)


# Define the DAG
with DAG('modeler',
          description='modeler', 
          schedule_interval='0 0 * * *', 
          start_date=datetime(2024, 10, 7), 
          catchup=False) as dag:

    task = PythonOperator(task_id='modeling_task',
                        python_callable=handler,
                        dag=dag)
