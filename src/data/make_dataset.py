import kagglehub
import pandas as pd
from sklearn.model_selection import train_test_split
import os
import sys
import great_expectations as ge
from .great_expectations_validation import create_expectation_suite

TARGET_COLUMN = 'default.payment.next.month'


def basic_clean_data(target_df: pd.DataFrame, data_path: str) -> pd.DataFrame:

    target_df = target_df.copy()
    target_df.columns = [column.strip() for column in target_df.columns]
    
    if TARGET_COLUMN in target_df.columns:
        target_df[TARGET_COLUMN] = pd.to_numeric(target_df[TARGET_COLUMN], errors="coerce").astype("Int64")
    else:
        sys.exit(f"В данных отстутсвует таргет колонка {TARGET_COLUMN}. Проверьте данные в папке {data_path}.")

    target_df = target_df.drop("ID", axis=1, errors="ignore")

    for column in target_df.columns:
        if column == TARGET_COLUMN:
            continue
        if pd.api.types.is_numeric_dtype(target_df[column]):
            if target_df[column].isna().any():
                target_df[column] = target_df[column].fillna(target_df[column].median())
        else:
            if target_df[column].isna().any():
                target_df[column] = target_df[column].fillna(target_df[column].mode(dropna=True).iloc[0])

    return target_df

def load_and_split_data(data_path: str) -> bool:
    print('='*50)
    print('Загружаем данные для формирования выборок')
    print('='*50, end='\n\n')
    if os.path.exists(data_path):
        credit_card_df = pd.read_csv(data_path)
        credit_card_df = basic_clean_data(credit_card_df, data_path)
        print('='*50)
        print('Создаем правила для обработки входных данных')
        suite = create_expectation_suite()
        print('Правила сформированы и записаны')
        print('='*50, end='\n\n')

        print('='*50)
        print('Проверяем данные')
        validator = ge.from_pandas(
            pandas_df=credit_card_df, 
            expectation_suite=suite 
        )

        results = validator.validate()
        for result in results.results:
            if not result.success:
                print('='*25)
                print('Ошибка проверки данных')
                print(f'Тип проверки: {result["expectation_config"]["expectation_type"]}')
                print(f'Колонка: {result["expectation_config"]["kwargs"]["column"]}')
                print(f"Нарушено: {result.result}")
                return False
        print(f"Все проверки пройдены: {results.success}")
        print(f"Успешно: {results.statistics['success_percent']:.1f}%")
        print('='*50, end='\n\n')

        print('='*50)
        print('Создаем тренировочную и тестовую выборки')
        train, test = train_test_split(credit_card_df, test_size=0.2, random_state=42)
        X_train = train.drop('default.payment.next.month', axis=1)
        Y_train = train['default.payment.next.month']
        X_test = test.drop('default.payment.next.month', axis=1)
        Y_test = test['default.payment.next.month']
        X_train.to_csv("data/processed/x_train.csv", index=False)
        Y_train.to_csv("data/processed/y_train.csv", index=False)
        X_test.to_csv("data/processed/x_test.csv", index=False)
        Y_test.to_csv("data/processed/y_test.csv", index=False)
        print('Тестовая и тренировочная выборки созданы')
        print('='*50, end='\n\n')
        return True
    else:
        print("Неверный путь к файлу UCI_Credit_Card.csv, или его не существует по заданному пути.")
        return False
    