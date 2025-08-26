# src/features/build_features.py
from typing import Tuple, Optional
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import joblib

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create domain-specific features and return new dataframe."""
    df = df.copy()
    # Example: BMI bins (if BMI column exists)
    if "BMI" in df.columns:
        df["bmi_cat"] = pd.cut(df["BMI"], bins=[0, 18.5, 25, 30, 100],
                               labels=["underweight", "normal", "overweight", "obese"])
    # Example: Age group
    df["age_group"] = pd.cut(df["age"], bins=[0, 35, 50, 65, 120],
                             labels=["young","adult","middle","senior"])
    # Convert categorical to ordinal/simple encoding (you can expand)
    df = pd.get_dummies(df, columns=["bmi_cat","age_group"], drop_first=True)
    return df

def scale_features(df: pd.DataFrame, scaler: Optional[StandardScaler] = None,
                   save_path: Optional[str] = None) -> Tuple[pd.DataFrame, StandardScaler]:
    """Scale numeric features with StandardScaler."""
    num_cols = df.select_dtypes(include="number").columns.tolist()
    # do not scale target if present
    num_cols = [c for c in num_cols if c != "TenYearCHD"]
    if scaler is None:
        scaler = StandardScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])
    else:
        df[num_cols] = scaler.transform(df[num_cols])

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(scaler, save_path)

    return df, scaler
