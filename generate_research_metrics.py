import json
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import LinearSVR

DATASET_PATH = "dataset/ielts_writing_dataset.csv"

df = pd.read_csv(DATASET_PATH)
df = df[["Question", "Essay", "Overall"]].dropna()

df["text"] = df["Question"].astype(str) + " " + df["Essay"].astype(str)

X = df["text"]
y = df["Overall"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

models = {
    "Ridge Regression": Ridge(),
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "Linear SVR": LinearSVR(random_state=42, max_iter=5000)
}

results = []

best_model = None
best_mae = float("inf")
best_model_name = ""

for name, regressor in models.items():
    print(f"Training {name}...")

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=20000,
            ngram_range=(1, 2),
            stop_words="english"
        )),
        ("regressor", regressor)
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    rounded_predictions = np.round(predictions * 2) / 2

    mae = mean_absolute_error(y_test, rounded_predictions)
    rmse = mean_squared_error(y_test, rounded_predictions) ** 0.5
    exact_accuracy = np.mean(y_test.values == rounded_predictions)
    within_half_accuracy = np.mean(np.abs(y_test.values - rounded_predictions) <= 0.5)

    results.append({
        "model": name,
        "mae": round(float(mae), 3),
        "rmse": round(float(rmse), 3),
        "exact_accuracy": round(float(exact_accuracy * 100), 2),
        "within_half_accuracy": round(float(within_half_accuracy * 100), 2)
    })

    if mae < best_mae:
        best_mae = mae
        best_model = model
        best_model_name = name

results = sorted(results, key=lambda x: x["mae"])

research_data = {
    "dataset_size": int(len(df)),
    "training_size": int(len(X_train)),
    "test_size": int(len(X_test)),
    "best_model": best_model_name,
    "results": results
}

with open("model_metrics.json", "w") as f:
    json.dump(research_data, f, indent=4)

joblib.dump(best_model, "ielts_score_model.pkl")

print("Research metrics saved to model_metrics.json")
print("Best model saved as ielts_score_model.pkl")
