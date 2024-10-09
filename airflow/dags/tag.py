import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri('http://mlflow:5000')
client = MlflowClient()

def set_experiment(experiment_name: str):
    mlflow.set_experiment(experiment_name=experiment_name)

def model_register(model_name, run_id):
    model_uri = f'runs:/{run_id}/model'
    model_version = mlflow.register_model(model_uri, model_name)

    return model_version

def promote_to_production(model_name, version):
    for m in client.search_model_versions(f"name = '{model_name}' and tags.stage = 'production'"):
        print(m)
        archive_model(model_name, m.version)

    client.set_model_version_tag(
        name=model_name,
        version=version,
        key='stage',
        value='production',
    )

    print(f'Model: {model_name}, Version: {version} promoted to Production...')

def archive_model(model_name, version):
    client.set_model_version_tag(
        name=model_name,
        version=version,
        key='stage',
        value='archived'
    )

    print(f'Model: {model_name}, Version: {version} promoted to Archive...')


def run(experiment_name: str):
    return mlflow.start_run(run_name=experiment_name, nested=True)

def log_model(experiment_name: str, python_model):
    mlflow.pyfunc.log_model(
        f'{experiment_name}',
        python_model=python_model
    )

class ALSWrapper(mlflow.pyfunc.PythonModel):
    def __init__(self, model):
        self.model = model

    def load_context(self, context):
        pass

    def predict(self, context, model_input):
        return self.model.recommend(model_input)
