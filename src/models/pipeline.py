from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (
    make_scorer,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
)
import pandas as pd


def get_best_pipeline(
    numeric_column: list[str],
    categorical_column: list[str],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_name: str,
):
    random_state = 42
    models = {
        "LogisticRegression": {
            "model": LogisticRegression(random_state=random_state),
            "param_distributions": {
                "classifier__C": [0.01, 0.1, 1, 10, 100],
                "classifier__penalty": ["l1", "l2", "elasticnet"],
                "classifier__solver": ["liblinear", "saga"],
                "classifier__class_weight": [
                    None,
                    "balanced",
                    {0: 1, 1: 3},
                    {0: 1, 1: 5},
                    {0: 1, 1: 8},
                    {0: 1, 1: 10},
                ],
            },
        },
        "GradientBoostingClassifier": {
            "model": GradientBoostingClassifier(random_state=random_state),
            "param_distributions": {
                "classifier__n_estimators": [100, 200, 300],
                "classifier__learning_rate": [0.01, 0.05, 0.1],
                "classifier__max_depth": [3, 5, 7],
                "classifier__min_samples_split": [2, 5, 10],
                "classifier__subsample": [0.8, 0.9, 1.0],
            },
        },
        "RandomForestClassifier": {
            "model": RandomForestClassifier(random_state=random_state),
            "param_distributions": {
                "classifier__n_estimators": [300, 400, 500],
                "classifier__max_depth": [20, 25, None],
                "classifier__min_samples_leaf": [1, 2],
                "classifier__max_features": ["sqrt", "log2"],
                "classifier__class_weight": [
                    "balanced_subsample",
                    {0: 1, 1: 3},
                    {0: 1, 1: 5},
                    {0: 1, 1: 8},
                    {0: 1, 1: 10},
                ],
                "classifier__max_samples": [0.7, 0.8, 0.9],
            },
        },
    }

    if models.get(model_name) == None:
        raise ValueError(
            f"Неверное имя модели. Доступные названия моделей: {list(models.keys())}"
        )

    random_state = 42
    print("=" * 50)
    print(f"Создаем Pipeline для предобработки и обучения модели {model_name}")
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value=-1)),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_column),
            ("cat", categorical_transformer, categorical_column),
        ]
    )
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", models[model_name]["model"]),
        ]
    )

    scoring = {
        "roc_auc": "roc_auc",
        "precision": make_scorer(precision_score, average="binary"),
        "recall": make_scorer(recall_score, average="binary"),
        "f1": make_scorer(f1_score, average="binary"),
    }

    print(
        "Реализуем автоматический подбор гиперпараметров с помощью RandomizedSearchCV"
    )

    random_search = RandomizedSearchCV(
        pipeline,
        param_distributions=models[model_name]["param_distributions"],
        n_iter=30,
        scoring=scoring,
        refit="f1",
        cv=5,
        n_jobs=-1,
        random_state=random_state,
        verbose=1,
    )

    print("Обучаем нашу модель с разными параметрами и находим лучшие")
    random_search.fit(X_train, y_train)

    # Результаты
    print(f"Лучшие параметры: {random_search.best_params_}")
    print(f"Лучший F1-score: {random_search.best_score_:.3f}")

    best_idx = random_search.best_index_

    model_log = {
        "best_params": random_search.best_params_,
        "metrics": {
            "best_roc_auc": random_search.cv_results_["mean_test_roc_auc"][best_idx],
            "best_precision": random_search.cv_results_["mean_test_precision"][
                best_idx
            ],
            "best_recall": random_search.cv_results_["mean_test_recall"][best_idx],
            "best_f1": random_search.cv_results_["mean_test_f1"][best_idx],
        },
    }

    best_pipeline = random_search.best_estimator_

    print("Модель готова для предсказывания")

    best_pipeline.fit(X_train, y_train)

    print("=" * 50, end="\n\n")
    return best_pipeline, model_log
