import requests

def handler(ti, **kwargs):
    prev_task_data = ti.xcom_pull(task_ids='modeling_task')
    print('prev_task_data')
    print(prev_task_data)

    name = prev_task_data['name']
    version = prev_task_data['version']
    experiment_name = prev_task_data['experiment_name']

    url = f'http://api:8000/experiment/{experiment_name}/version'

    data = {
        'model': name,
        'version': version,
        'source': prev_task_data['source'],
    }
    
    print(f'request url: {url}')
    response = requests.post(url, json=data)

    print(response.json())
