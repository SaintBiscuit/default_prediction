from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import subprocess


def check_drift_and_decide(**kwargs):
    script_path = "monitoring/monitor_drift.py"
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

    if "drift detected" in result.stdout.lower() or "PSI" in result.stdout:
        return "retrain_model"
    else:
        return "no_retrain_needed"


# Функция переобучения модели
def retrain_model():
    print("Запуск переобучения модели...")
    train_script = "src/models/train_pipeline_with_onxx.py"
    subprocess.run(["python", train_script], check=True)
    print("Модель переобучена и сохранена в models/new_model.onnx")


# Функция тестирования новой модели
def test_new_model():
    print("Тестирование новой модели...")
    subprocess.run(["pytest", "tests"], check=True)
    print("Тесты пройдены")


# Функция деплоя новой модели
def deploy_new_model():
    print("Деплой новой версии модели в K8s...")
    subprocess.run(
        [
            "kubectl",
            "set",
            "image",
            "deployment/credit-scoring-api",
            "api=cr.yandex/crp64qbt432vtdkce0rj/credit-scoring-api:new-version",
            "--kubeconfig",
            "deployment/kubeconfig.yaml",
        ],
        check=True,
    )
    print("Новая версия задеплоена")


with DAG(
    dag_id="credit_scoring_retrain",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@monthly",
    catchup=False,
    tags=["mlops", "credit-scoring", "retraining"],
    default_args={
        "owner": "nadezhda",
        "retries": 1,
    },
) as dag:

    drift_check = BranchPythonOperator(
        task_id="check_drift",
        python_callable=check_drift_and_decide,
        provide_context=True,
    )

    retrain = PythonOperator(task_id="retrain_model", python_callable=retrain_model)

    test = PythonOperator(task_id="test_new_model", python_callable=test_new_model)

    deploy = PythonOperator(
        task_id="deploy_new_model", python_callable=deploy_new_model
    )

    no_retrain = BashOperator(
        task_id="no_retrain_needed",
        bash_command='echo "Дрифт не обнаружен — переобучение не требуется"',
    )

    drift_check >> [retrain, no_retrain]
    retrain >> test >> deploy
