import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import LinearSVR
from sklearn.metrics import mean_absolute_error

DATASET_PATH = "dataset/ielts_writing_dataset.csv"

df = pd.read_csv(DATASET_PATH)
df = df[["Question", "Essay", "Overall"]].dropna()

df["text"] = df["Question"].astype(str) + "\n\n" + df["Essay"].astype(str)

X = df["text"]
y = df["Overall"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

models = {
    "Ridge Regression": Ridge(),
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(
        n_estimators=100,
        random_state=42
    ),
    "Linear SVR": LinearSVR(
        random_state=42,
        max_iter=10000
    )
}

results = []

best_model = None
best_model_name = None
best_mae = float("inf")

for name, regressor in models.items():
    print(f"\nTraining {name}...")

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

    rounded_predictions = [round(p * 2) / 2 for p in predictions]

    mae = mean_absolute_error(y_test, rounded_predictions)

    exact_accuracy = sum(
        p == r for p, r in zip(rounded_predictions, y_test)
    ) / len(y_test)

    within_half = sum(
        abs(p - r) <= 0.5 for p, r in zip(rounded_predictions, y_test)
    ) / len(y_test)

    print("MAE:", round(mae, 3))
    print("Exact Accuracy:", round(exact_accuracy * 100, 2), "%")
    print("±0.5 Accuracy:", round(within_half * 100, 2), "%")

    results.append({
        "Model": name,
        "MAE": mae,
        "Exact Accuracy": exact_accuracy,
        "±0.5 Accuracy": within_half
    })

    if mae < best_mae:
        best_mae = mae
        best_model = model
        best_model_name = name

results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by="MAE")

print("\n===== MODEL COMPARISON =====")
print(results_df)

print("\nBest model:", best_model_name)
print("Best MAE:", round(best_mae, 3))

joblib.dump(best_model, "ielts_score_model.pkl")

print("\nBest model saved as ielts_score_model.pkl")
