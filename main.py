from src.data.make_dataset import load_and_split_data
from src.data.great_expectations_validation import create_expectation_suite
from mode import train_pipeline


load_and_split_data('data/raw/UCI_Credit_Card.csv')
train_pipeline('LogisticRegression')
train_pipeline('GradientBoostingClassifier')
train_pipeline('RandomForestClassifier')