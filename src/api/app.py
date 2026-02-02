import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from src.data.make_dataset import load_and_split_data
from src.models.train_pipeline import train_pipeline

app = FastAPI(title="Credit Default Prediction API")

model = None


class ClientData(BaseModel):
    LIMIT_BAL: float
    SEX: int
    EDUCATION: int
    MARRIAGE: int
    AGE: int

    PAY_0: int
    PAY_2: int
    PAY_3: int
    PAY_4: int
    PAY_5: int
    PAY_6: int

    BILL_AMT1: float
    BILL_AMT2: float
    BILL_AMT3: float
    BILL_AMT4: float
    BILL_AMT5: float
    BILL_AMT6: float

    PAY_AMT1: float
    PAY_AMT2: float
    PAY_AMT3: float
    PAY_AMT4: float
    PAY_AMT5: float
    PAY_AMT6: float


@app.lifespan("startup")
def load_model():
    global model
    load_and_split_data("data/raw/UCI_Credit_Card.csv")
    logreg_model = train_pipeline("LogisticRegression")
    grad_model = train_pipeline("GradientBoostingClassifier")
    randfor_model = train_pipeline("RandomForestClassifier")
    best_fi = 0
    best_model_path = None
    for model in [logreg_model, grad_model, randfor_model]:
        metrics = model[0]
        if metrics["best_f1"] >= best_fi:
            best_model_path = model[1]
    model = joblib.load(best_model_path)


@app.get("/")
def root():
    return {"message": "Credit Default Prediction API is working!"}


@app.post("/predict")
def predict(data: ClientData):
    input_data = pd.DataFrame([data.model_dump()])
    proba = float(model.predict_proba(input_data)[0][1])
    pred = int(proba >= 0.5)
    return {"default_prediction": pred, "default_probability": proba}
