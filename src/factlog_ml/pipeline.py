"""Model training and evaluation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .nasa_cmapss import CMAPSSSplit


@dataclass(frozen=True)
class TrainedEvaluation:
    metrics: Dict[str, float]
    model_name: str
    model_version: str


def build_classifier(random_state: int = 42) -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=500,
                    class_weight="balanced",
                    random_state=random_state,
                ),
            ),
        ]
    )


def train_and_evaluate(train_split: CMAPSSSplit, test_split: CMAPSSSplit) -> TrainedEvaluation:
    pipeline = build_classifier()
    pipeline.fit(train_split.features, train_split.labels)

    predictions = pipeline.predict(test_split.features)
    probabilities = pipeline.predict_proba(test_split.features)[:, 1]

    metrics = {
        "accuracy": round(float(accuracy_score(test_split.labels, predictions)), 4),
        "precision": round(float(precision_score(test_split.labels, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(test_split.labels, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(test_split.labels, predictions, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(test_split.labels, probabilities)), 4),
        "predicted_positive_ratio": round(float(np.mean(predictions)), 4),
    }

    classifier = pipeline.named_steps["classifier"]
    model_name = type(classifier).__name__
    model_version = "logistic-regression-balanced-v1"

    return TrainedEvaluation(
        metrics=metrics,
        model_name=model_name,
        model_version=model_version,
    )
