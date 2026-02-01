import mlflow
import mlflow.sklearn
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt
import pandas as pd
import os
import joblib
from .pipeline import get_best_pipeline
from datetime import datetime
import pandas as pd
import json


def train_pipeline(model_name: str):
    X_train = pd.read_csv('data/processed/x_train.csv')
    y_train = pd.read_csv('data/processed/y_train.csv')
    X_test = pd.read_csv('data/processed/x_test.csv')
    y_test = pd.read_csv('data/processed/y_test.csv')

    # Определение признаков
    numeric_features = ['LIMIT_BAL', 'AGE', 'BILL_AMT1', 'PAY_AMT1']
    categorical_features = ['EDUCATION', 'MARRIAGE', 'PAY_0']

    with mlflow.start_run():
        best_pipeline, model_log = get_best_pipeline(numeric_features, categorical_features, X_train, y_train, model_name)

        # Предсказания и метрики
        y_pred_proba = best_pipeline.predict_proba(X_test)[:, 1]

        # Логирование в MLflow
        mlflow.log_param("model_type", model_name)
        mlflow.log_params(model_log['best_params'])
        mlflow.log_metrics(model_log['metrics'])

        # ROC-кривая
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        plt.figure()
        plt.plot(fpr, tpr, label=f'ROC-AUC = {model_log["metrics"]["best_roc_auc"]:.2f})')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel('Доля ложно полижетельных результатов')
        plt.ylabel('Доля истинно положительных результатов')
        plt.title('ROC кривая')
        plt.legend(loc="lower right")
        plt.savefig(f"graphs/{model_name}_roc_curve.png")
        mlflow.log_artifact(f"graphs/{model_name}_roc_curve.png")

        # Сохранение модели
        mlflow.sklearn.log_model(best_pipeline, "model")
        model_path = f"models/{model_name}_credit_default_model.pkl"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(best_pipeline, model_path) 
        mlflow.log_artifact(model_path)

        # Сохранение метрик
        with open("metrics.json", "a") as f:
            model_metrics = {
                'model_name': model_name,
                'timestamp': str(datetime.now()),
                **model_log['metrics']
            }
            f.write(json.dumps(model_metrics) + "\n")
    
    return model_log['metrics'], model_path
