from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

import warnings; warnings.filterwarnings('ignore')
import asl
import log_to_mlflow
import notify_to_api_server

def create_model():
    wrapped_model = asl.handler('dummy_suffix')
    
# mlflow 설정
    print('configure mlflow')
    dataset_name = '2099-12-31'
    experiment_name = f'ALS_{dataset_name}'
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
