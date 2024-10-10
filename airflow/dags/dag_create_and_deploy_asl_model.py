from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

import warnings; warnings.filterwarnings('ignore')
import asl
import log_to_mlflow
import notify_to_api_server
import preprocess_movie_dt
import get_latest_dataset

## TODO: 모델 마다 파일을 분리하는 걸 추천 수정되어야하는 부분은 TODO: 처리해두
def create_model():
    (movie_dt, rating_dt) = get_latest_dataset.handler()
    movie_dt = preprocess_movie_dt.handler(movie_dt)

    # 'id' 열을 정수형으로 변환
    movie_dt['id'] = movie_dt['id'].astype(int)
    rating_dt['tmdbId'] = rating_dt['tmdbId'].astype(int)

    wrapped_model = asl.handler(movie_dt, rating_dt)
    
    # mlflow 설정: 추가 모델 설정시 아래 변수들에 대한 동적 설정 혹은 dag 분리
    print('configure mlflow')
    # TODO: 여러 모델을 **동시**에 운영하고자 할때는 model_name 을 변경할 필요 있음
    #       다만 이 경우에는 api server 의 api 도 확장 필요
    experiment_name = f'ALS_movie_recommendation'
    model_name = 'movie ALS'

    return log_to_mlflow.handler(wrapped_model, experiment_name, model_name)

# TODO: DAG 이름은 유일해야하므로 수정 요구됨
with DAG('create_and_deploy_asl_model',
          description='create asl model and deploy', 
          schedule_interval='0 0 * * *', 
          start_date=datetime(2024, 10, 7), 
          dagrun_timeout=timedelta(hours=2),
          catchup=False) as dag:

    task1 = PythonOperator(task_id='modeling_task',
                        python_callable=create_model,
                        dag=dag)


    task2 = PythonOperator(task_id='notify_to_api_server',
                        python_callable=notify_to_api_server.handler,
                        dag=dag)


task1 >> task2
