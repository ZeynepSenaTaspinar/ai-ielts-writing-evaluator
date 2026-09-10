import os
import re

import pandas as pd
from openai import OpenAI

api_key = os.environ.get("OPENAI_API_KEY", "").strip()
if not api_key:
    raise RuntimeError("Set OPENAI_API_KEY to run this evaluation script.")

client = OpenAI(api_key=api_key)

DATASET_PATH = "dataset/ielts_writing_dataset.csv"

df = pd.read_csv(DATASET_PATH)
df = df[["Question", "Essay", "Overall"]].dropna()

# sadece 5 örnekle test edelim (yoksa çok para gider)
df = df.head(5)

def get_ai_score(question, essay):
    prompt = f"""
You are an expert IELTS Writing examiner.

Evaluate the essay using IELTS Writing band descriptors.

Important:
- Do NOT always give 5.0.
- Use the full IELTS band range.
- Strong essays can receive 7.0, 7.5, 8.0 or higher.
- Weak essays can receive below 5.0.
- Judge based on the actual quality of the essay.
- Return ONLY one overall band score.
- The score must be one of: 0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0

Criteria:
1. Task Response
2. Coherence and Cohesion
3. Lexical Resource
4. Grammatical Range and Accuracy

Question:
{question}

Essay:
{essay}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a strict but fair IELTS Writing examiner."},
            {"role": "user", "content": prompt}
        ]
    )

    text = response.choices[0].message.content.strip()

    match = re.search(r"\d+(\.\d+)?", text)
    if match:
        return float(match.group())
    return None


results = []

for i, row in df.iterrows():
    print(f"\nEvaluating {i+1}/{len(df)}")

    question = row["Question"]
    essay = row["Essay"]
    real_score = row["Overall"]

    ai_score = get_ai_score(question, essay)

    if ai_score is None:
        continue

    error = abs(ai_score - real_score)

    print(f"Real: {real_score} | AI: {ai_score} | Error: {error}")

    results.append(error)


# METRICS
if results:
    mae = sum(results) / len(results)
    exact = sum(1 for e in results if e == 0) / len(results)
    half = sum(1 for e in results if e <= 0.5) / len(results)

    print("\n===== RESULTS =====")
    print("MAE:", round(mae, 3))
    print("Exact Accuracy:", round(exact * 100, 2), "%")
    print("±0.5 Accuracy:", round(half * 100, 2), "%")
