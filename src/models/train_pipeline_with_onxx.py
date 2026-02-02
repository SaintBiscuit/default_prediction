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
from onxx_transformation.convert_to_onxx import convert_to_onxx
from onxx_transformation.quantization_onxx import quantization_model
from .train_pipeline import train_pipeline


def train_pipeline_with_onxx(model_name):
    metrics, model_path = train_pipeline(model_name)
    convert_to_onxx(model_path=model_path)

    
if __name__ == "__main__":
    train_pipeline_with_onxx('RandomForestClassifier')
    quantization_model()
