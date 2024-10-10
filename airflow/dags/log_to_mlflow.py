import tag

def handler(wrapped_model, experiment_name: str, model_name: str):
    tag.set_experiment(experiment_name)

    print('log to mlflow')
    with tag.run(experiment_name) as run:
        tag.log_model(experiment_name, python_model=wrapped_model)

        print(f'register model, run: {run.info.run_id}')
        model_version = tag.model_register(model_name, run.info.run_id)
        print(f'model version: {model_version}')

        print(f'give model a version, model_version: {model_version.version}')
        tag.promote_to_production(model_name, model_version.version)

        ret = dict(model_version)
        ret['experiment_name'] = experiment_name

        return ret


