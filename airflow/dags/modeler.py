from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

import mlflow.sklearn
import pandas as pd
import numpy as np
import pickle
import ast
import warnings; warnings.filterwarnings('ignore')

from io import BytesIO
from sklearn.metrics.pairwise import cosine_similarity 
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix

def handler():
    print('load data')
    movie_path = 'src/datasets/movies_metadata.csv'
    rating_path = 'src/datasets/ratings_small.csv'
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

#+ mlflow 설정
    print('configure mlflow')
    dataset_name = '2099-12-31'
    experiment_name = f'ALS_{dataset_name}'

    mlflow.set_tracking_uri('http://mlflow:5001')
    mlflow.set_experiment(experiment_name=experiment_name )
#- mlflow 설정


    print('log to mlflow')
    with mlflow.start_run(run_name=experiment_name, nested=True) as run:
        class ALSWrapper(mlflow.pyfunc.PythonModel):
            def load_context(self, context):
                self.model = model  # 모델 로드

            def predict(self, context, model_input):
                # 예시 예측 (사용자 정의 예측 로직 적용)
                return self.model.recommend(model_input)

        mlflow.pyfunc.log_model(
            f'{experiment_name}',
            python_model=ALSWrapper()
        )



# Define the DAG
with DAG('modeler',
          description='modeler', 
          schedule_interval='0 0 * * *', 
          start_date=datetime(2024, 10, 7), 
          catchup=False) as dag:

    task = PythonOperator(task_id='modeling_task',
                        python_callable=handler,
                        dag=dag)
