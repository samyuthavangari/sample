import importlib

pkgs = ["numpy","pandas","sklearn","matplotlib","seaborn","scipy","statsmodels"]
missing = []
for p in pkgs:
    try:
        importlib.import_module(p)
    except Exception as e:
        missing.append((p, str(e)))
if missing:
    raise SystemExit(f"Missing or error in: {missing}")
print("✅ Environment check passed.")
