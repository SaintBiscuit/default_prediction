import pandas as pd
from evidently.report import Report
from evidently.metrics import DataDriftTable, DatasetDriftMetric
from evidently.metrics import (
    ClassificationPRCurve,
    ClassificationConfusionMatrix,
    ClassificationClassBalance,
)

# Загрузка данных
train_data = pd.read_csv("data/processed/train.csv")
test_data = pd.read_csv("data/processed/test.csv")

# Target колонка
target = "default.payment.next.month"
prediction = "prediction"

# Dummy предсказания
train_data[prediction] = train_data[target]  # имитация идеальной модели на train
test_data[prediction] = test_data[target]  # имитация на test (для демонстрации decay)

# Data drift report
data_drift_report = Report(metrics=[DataDriftTable(), DatasetDriftMetric()])

data_drift_report.run(
    reference_data=train_data.drop(columns=[target, prediction]),
    current_data=test_data.drop(columns=[target, prediction]),
)
data_drift_report.save_html("monitoring/data_drift_report.html")
print("Data drift report saved")

# Concept drift + performance decay report
performance_report = Report(
    metrics=[
        ClassificationPRCurve(),
        ClassificationConfusionMatrix(),
        ClassificationClassBalance(),
    ]
)

performance_report.run(
    reference_data=train_data[[target, prediction]],
    current_data=test_data[[target, prediction]],
)
performance_report.save_html("monitoring/performance_decay_report.html")
print("Performance decay report saved")
