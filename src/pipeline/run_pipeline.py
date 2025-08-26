# src/pipeline/run_pipeline.py
import typer
import logging
from pathlib import Path
from src.data.preprocess import load_raw, basic_clean, impute_numeric, split_save
from src.features.build_features import build_features, scale_features
logger = logging.getLogger(__name__)
app = typer.Typer()

@app.command()
def run(input_csv: str = "data/raw/framingham.csv",
        processed_dir: str = "data/processed",
        model_path: str = "models/random_forest.joblib",
        scaler_path: str = "models/scaler.joblib"):
    # 1. Load & clean
    df = load_raw(input_csv)
    df = basic_clean(df)
    df = impute_numeric(df)

    # 2. Optional: feature engineering
    df = build_features(df)

    # 3. split
    train, val, test = split_save(df, target_col="TenYearCHD", out_dir=processed_dir)

    # 4. scale
    X_train = train.drop(columns=["TenYearCHD"])
    y_train = train["TenYearCHD"]

    X_train_scaled, scaler = scale_features(X_train, save_path=scaler_path)
    X_test = test.drop(columns=["TenYearCHD"])
    y_test = test["TenYearCHD"]
    X_test_scaled, _ = scale_features(X_test, scaler=scaler)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app()
