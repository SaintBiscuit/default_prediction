import joblib
from skl2onnx import to_onnx
import numpy as np
import pandas as pd
import os
from src.data.make_dataset import load_and_split_data
from src.models.train_pipeline import train_pipeline


# Путь к модели
model_path = None
if not os.path.exists("models/RandomForestClassifier_credit_default_model.pkl"):
    load_and_split_data("data/raw/UCI_Credit_Card.csv")
    _, model_path = train_pipeline("RandomForestClassifier")
else:
    model_path = "models/RandomForestClassifier_credit_default_model.pkl"
model = joblib.load(model_path)

feature_names = [
    "LIMIT_BAL",
    "SEX",
    "EDUCATION",
    "MARRIAGE",
    "AGE",
    "PAY_0",
    "PAY_2",
    "PAY_3",
    "PAY_4",
    "PAY_5",
    "PAY_6",
    "BILL_AMT1",
    "BILL_AMT2",
    "BILL_AMT3",
    "BILL_AMT4",
    "BILL_AMT5",
    "BILL_AMT6",
    "PAY_AMT1",
    "PAY_AMT2",
    "PAY_AMT3",
    "PAY_AMT4",
    "PAY_AMT5",
    "PAY_AMT6",
]

num_features = len(feature_names)

# Dummy input как DataFrame с именами колонок
dummy_input = pd.DataFrame(
    np.random.randn(1, num_features).astype(np.float32), columns=feature_names
)

# Конвертация в ONNX
onnx_model = to_onnx(model, dummy_input, target_opset=13)

# Сохранение
onnx_path = "models/model.onnx"
with open(onnx_path, "wb") as f:
    f.write(onnx_model.SerializeToString())

# Инфо о размерах для отчёта (benchmark)
pkl_size = os.path.getsize(model_path) / (1024 * 1024)
onnx_size = os.path.getsize(onnx_path) / (1024 * 1024)

print(f"Конвертация успешна! ONNX-модель сохранена: {onnx_path}")
print(f"Размер исходной модели (.pkl): {pkl_size:.2f} MB")
print(f"Размер ONNX-модели: {onnx_size:.2f} MB")
