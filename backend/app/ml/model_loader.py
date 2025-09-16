import os, joblib

BASE_DIR = os.path.dirname(__file__)

def load_model(name="logreg"):
    path_map = {
        "logreg": os.path.join(BASE_DIR, "logreg_model.joblib"),
        "rf": os.path.join(BASE_DIR, "rf_model.joblib"),
        "svm": os.path.join(BASE_DIR, "svm_model.joblib"),
        "nn": os.path.join(BASE_DIR, "nn_model.joblib"),
    }
    model_path = path_map.get(name, path_map["logreg"])
    return joblib.load(model_path)
