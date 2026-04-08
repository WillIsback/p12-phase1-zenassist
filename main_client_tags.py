"""Train & export ML model using the client's raw CFPB tag selection (12 classes).

This script mirrors main.py but replaces the consolidated 11-label taxonomy
with the 12 tags chosen by the client.  Old CFPB tag variants are mapped to
their modern equivalents; credit-reporting tags are excluded (out of scope
for the client).
"""

import argparse
from pathlib import Path

import pandas as pd

from main import (
    RANDOM_STATE,
    TARGET_COL,
    TEXT_COL,
    build_features,
    evaluate_models,
    export_artifacts,
    get_classifiers,
    sha256_file,
)

# ── Client tag mapping ──────────────────────────────────────────────────────
# 16 raw dataset values → 12 client-chosen classes.
# Rows whose raw tag is NOT a key here (i.e. the two credit-reporting
# variants) are dropped — the client excluded credit reporting entirely.

CLIENT_LABEL_MAP: dict[str, str] = {
    # Direct matches (tags already in client list)
    "Debt collection": "Debt collection",
    "Consumer Loan": "Consumer Loan",
    "Credit card or prepaid card": "Credit card or prepaid card",
    "Mortgage": "Mortgage",
    "Vehicle loan or lease": "Vehicle loan or lease",
    "Student loan": "Student loan",
    "Payday loan, title loan, or personal loan": "Payday loan, title loan, or personal loan",
    "Checking or savings account": "Checking or savings account",
    "Bank account or service": "Bank account or service",
    "Money transfer, virtual currency, or money service": "Money transfer, virtual currency, or money service",
    "Money transfers": "Money transfers",
    # Old CFPB variants → modern equivalents kept by the client
    "Credit card": "Credit card or prepaid card",
    "Prepaid card": "Credit card or prepaid card",
    "Payday loan": "Payday loan, title loan, or personal loan",
    # Client consolidation (rare tags absorbed)
    "Other financial service": "Other financial services",
    "Virtual currency": "Other financial services",
    # EXCLUDED (not mapped → dropped):
    #   "Credit reporting, credit repair services, or other personal consumer reports"
    #   "Credit reporting"
}

DEFAULT_PICKLE_NAME = "best_ml_classifier_client.pkl"
DEFAULT_METRICS_NAME = "best_ml_metrics_client.json"


def load_dataset_client(dataset_path: Path) -> pd.DataFrame:
    df = pd.read_csv(dataset_path, low_memory=False)
    df = df.dropna(subset=[TARGET_COL, TEXT_COL]).copy()
    df["label"] = df[TARGET_COL].map(CLIENT_LABEL_MAP)
    df = df.dropna(subset=["label"]).reset_index(drop=True)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Train ML model with client tag selection")
    parser.add_argument("--dataset", required=True, help="Chemin vers data/dataset.csv")
    parser.add_argument("--output-dir", default="output", help="Dossier de sortie")
    parser.add_argument("--version", default="dev", help="Version ou tag Git")
    parser.add_argument("--pickle-name", default=DEFAULT_PICKLE_NAME)
    parser.add_argument("--metrics-name", default=DEFAULT_METRICS_NAME)
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    output_dir = Path(args.output_dir)

    df = load_dataset_client(dataset_path)
    features = build_features(df)
    trained_models, comparison_df = evaluate_models(
        classifiers=get_classifiers(),
        X_train=features["X_train"],
        X_test=features["X_test"],
        y_train=features["y_train"],
        y_test=features["y_test"],
    )

    best_model_name = str(comparison_df.iloc[0]["model"])
    best_model = trained_models[best_model_name]

    export_artifacts(
        output_dir=output_dir,
        best_model_name=best_model_name,
        best_model=best_model,
        vectorizer=features["vectorizer"],
        label_encoder=features["label_encoder"],
        comparison_df=comparison_df,
        dataset_path=dataset_path,
        version=args.version,
        dataset_row_count=len(df),
        train_row_count=len(features["X_train_text"]),
        test_row_count=len(features["X_test_text"]),
        pickle_name=args.pickle_name,
        metrics_name=args.metrics_name,
        label_consolidation_map=CLIENT_LABEL_MAP,
    )


if __name__ == "__main__":
    main()
