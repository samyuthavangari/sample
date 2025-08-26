# src/data/preprocess.py
from pathlib import Path
from typing import Tuple, Optional
import logging

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer

logger = logging.getLogger(__name__)

def load_raw(path: str) -> pd.DataFrame:
    """Load raw CSV into DataFrame."""
    p = Path(path)
    df = pd.read_csv(p)
    logger.info("Loaded raw data: %s rows, %s cols", *df.shape)
    return df

def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: strip column names, lower-case, drop full-empty rows."""
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(how="all")
    return df

def impute_numeric(df: pd.DataFrame, strategy: str = "median") -> pd.DataFrame:
    """Impute numeric missing values with SimpleImputer."""
    df = df.copy()
    num_cols = df.select_dtypes(include="number").columns
    imp = SimpleImputer(strategy=strategy)
    df[num_cols] = imp.fit_transform(df[num_cols])
    return df

def split_save(df: pd.DataFrame, target_col: str, out_dir: str,
               test_size: float = 0.2, val_size: float = 0.1,
               random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Create train/val/test splits (stratified) and save to out_dir.
    Returns (train, val, test)
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    X = df.drop(columns=[target_col])
    y = df[target_col]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=(test_size + val_size), stratify=y, random_state=random_state)

    relative_val_size = val_size / (test_size + val_size)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=relative_val_size, stratify=y_temp, random_state=random_state)

    train = pd.concat([X_train, y_train], axis=1)
    val = pd.concat([X_val, y_val], axis=1)
    test = pd.concat([X_test, y_test], axis=1)

    train.to_csv(out / "train.csv", index=False)
    val.to_csv(out / "val.csv", index=False)
    test.to_csv(out / "test.csv", index=False)

    logger.info("Saved train/val/test to %s", out)
    return train, val, test
