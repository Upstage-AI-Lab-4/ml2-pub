from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

import warnings; warnings.filterwarnings('ignore')
import asl
import log_to_mlflow
import notify_to_api_server
import preprocess_movie_dt
import get_latest_dataset

def create_model():
    (movie_dt, rating_dt) = get_latest_dataset.handler()
    movie_dt = preprocess_movie_dt.handler(movie_dt)
    wrapped_model = asl.handler(movie_dt, rating_dt)
    
    # mlflow 설정: 추가 모델 설정시 아래 변수들에 대한 동적 설정 혹은 dag 분리
    print('configure mlflow')
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
