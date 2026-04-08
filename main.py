import argparse
import json
import hashlib
import pickle
from datetime import datetime, UTC
from pathlib import Path

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

RANDOM_STATE = 42
TARGET_COL = "Tag"
TEXT_COL = "Consumer Claim"
CREDIT_REPORTING_LABEL = "Credit reporting"
CREDIT_CARD_LABEL = "Credit card"
BANK_ACCOUNT_LABEL = "Bank account"
PAYDAY_LOAN_LABEL = "Payday loan"
MONEY_TRANSFER_LABEL = "Money transfer"
OTHER_FINANCIAL_SERVICE_LABEL = "Other financial service"

ML_LABEL_CONSOLIDATION_MAP = {
    "Credit reporting, credit repair services, or other personal consumer reports": CREDIT_REPORTING_LABEL,
    "Credit reporting": CREDIT_REPORTING_LABEL,
    "Credit card": CREDIT_CARD_LABEL,
    "Credit card or prepaid card": CREDIT_CARD_LABEL,
    "Prepaid card": CREDIT_CARD_LABEL,
    "Bank account or service": BANK_ACCOUNT_LABEL,
    "Checking or savings account": BANK_ACCOUNT_LABEL,
    "Payday loan": PAYDAY_LOAN_LABEL,
    "Payday loan, title loan, or personal loan": PAYDAY_LOAN_LABEL,
    "Money transfer, virtual currency, or money service": MONEY_TRANSFER_LABEL,
    "Money transfers": MONEY_TRANSFER_LABEL,
    "Mortgage": "Mortgage",
    "Debt collection": "Debt collection",
    "Student loan": "Student loan",
    "Consumer Loan": "Consumer Loan",
    "Vehicle loan or lease": "Vehicle loan or lease",
    "Other financial service": OTHER_FINANCIAL_SERVICE_LABEL,
    "Virtual currency": OTHER_FINANCIAL_SERVICE_LABEL,
}

BEST_SVC_C = 0.01
BEST_SVC_CLASS_WEIGHT = "balanced"
DEFAULT_PICKLE_NAME = "best_ml_classifier.pkl"
DEFAULT_METRICS_NAME = "best_ml_metrics.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_dataset(dataset_path: Path) -> pd.DataFrame:
    df = pd.read_csv(dataset_path, low_memory=False)
    df = df.dropna(subset=[TARGET_COL, TEXT_COL]).copy()
    df["label"] = df[TARGET_COL].map(ML_LABEL_CONSOLIDATION_MAP)
    df = df.dropna(subset=["label"]).reset_index(drop=True)
    return df


def build_features(df: pd.DataFrame):
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["label"])

    x_train_text, x_test_text, y_train, y_test = train_test_split(
        df[TEXT_COL],
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    vectorizer = TfidfVectorizer(
        max_features=30_000,
        min_df=5,
        max_df=0.95,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )

    X_train = vectorizer.fit_transform(x_train_text)
    X_test = vectorizer.transform(x_test_text)

    return {
        "X_train": X_train,
        "X_test": X_test,
        "X_train_text": x_train_text,
        "X_test_text": x_test_text,
        "y_train": y_train,
        "y_test": y_test,
        "vectorizer": vectorizer,
        "label_encoder": label_encoder,
    }


def get_classifiers() -> dict:
    return {
        "DummyClassifier(most_frequent)": DummyClassifier(strategy="most_frequent", random_state=RANDOM_STATE),
        "ComplementNB": ComplementNB(alpha=0.1),
        "SGDClassifier(early_stopping)": SGDClassifier(
            loss="modified_huber",
            penalty="elasticnet",
            l1_ratio=0.15,
            alpha=1e-4,
            max_iter=1000,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=10,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        f"LinearSVC(C={BEST_SVC_C},cw={BEST_SVC_CLASS_WEIGHT})": LinearSVC(
            C=BEST_SVC_C,
            dual=False,
            class_weight=BEST_SVC_CLASS_WEIGHT,
            random_state=RANDOM_STATE,
        ),
    }


def evaluate_models(classifiers: dict, X_train, X_test, y_train, y_test) -> tuple[dict, pd.DataFrame]:
    trained_models = {}
    rows = []

    for name, clf in classifiers.items():
        clf.fit(X_train, y_train)
        trained_models[name] = clf

        y_pred_train = clf.predict(X_train)
        y_pred_test = clf.predict(X_test)

        accuracy_train = accuracy_score(y_train, y_pred_train)
        accuracy_test = accuracy_score(y_test, y_pred_test)
        f1_macro_train = f1_score(y_train, y_pred_train, average="macro", zero_division=0)
        f1_macro_test = f1_score(y_test, y_pred_test, average="macro", zero_division=0)
        f1_weighted_test = f1_score(y_test, y_pred_test, average="weighted", zero_division=0)
        f1_gap = f1_macro_train - f1_macro_test

        selection_score = f1_macro_test - 0.5 * f1_gap

        rows.append(
            {
                "model": name,
                "accuracy_train": float(accuracy_train),
                "accuracy_test": float(accuracy_test),
                "f1_macro_train": float(f1_macro_train),
                "f1_macro_test": float(f1_macro_test),
                "f1_weighted_test": float(f1_weighted_test),
                "f1_macro_gap": float(f1_gap),
                "selection_score": float(selection_score),
            }
        )

    comparison_df = pd.DataFrame(rows).sort_values("selection_score", ascending=False).reset_index(drop=True)
    return trained_models, comparison_df


def export_artifacts(
    output_dir: Path,
    best_model_name: str,
    best_model,
    vectorizer,
    label_encoder,
    comparison_df: pd.DataFrame,
    dataset_path: Path,
    version: str,
    dataset_row_count: int,
    train_row_count: int,
    test_row_count: int,
    pickle_name: str,
    metrics_name: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    model_artifact = {
        "model_name": best_model_name,
        "classifier": best_model,
        "vectorizer": vectorizer,
        "label_encoder": label_encoder,
        "text_column": TEXT_COL,
        "target_column": TARGET_COL,
        "label_column": "label",
        "label_consolidation_map": ML_LABEL_CONSOLIDATION_MAP,
        "selection_metrics": comparison_df.iloc[0].to_dict(),
        "version": version,
    }

    pickle_path = output_dir / pickle_name
    with pickle_path.open("wb") as handle:
        pickle.dump(model_artifact, handle)

    metrics_payload = {
        "version": version,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "dataset_path": str(dataset_path),
        "dataset_sha256": sha256_file(dataset_path),
        "dataset_row_count": dataset_row_count,
        "train_row_count": train_row_count,
        "test_row_count": test_row_count,
        "best_model_name": best_model_name,
        "metrics": comparison_df.iloc[0].to_dict(),
        "ranking": comparison_df.to_dict(orient="records"),
        "classes": list(label_encoder.classes_),
        "text_column": TEXT_COL,
        "target_column": TARGET_COL,
    }

    metrics_path = output_dir / metrics_name
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

    print(f"Pickle exporte: {pickle_path}")
    print(f"Metrics exportees: {metrics_path}")
    print(f"Modele retenu: {best_model_name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Chemin vers data/dataset.csv")
    parser.add_argument("--output-dir", default="output", help="Dossier de sortie")
    parser.add_argument("--version", default="dev", help="Version ou tag Git")
    parser.add_argument("--pickle-name", default=DEFAULT_PICKLE_NAME, help="Nom du fichier pickle exporte")
    parser.add_argument("--metrics-name", default=DEFAULT_METRICS_NAME, help="Nom du fichier JSON de metriques")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    output_dir = Path(args.output_dir)

    df = load_dataset(dataset_path)
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
    )


if __name__ == "__main__":
    main()