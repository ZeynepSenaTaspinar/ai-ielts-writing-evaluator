# AI IELTS Writing Evaluator

Hybrid IELTS Academic Writing Task 2 evaluator: a trained Random Forest model predicts a band score, a large language model writes examiner-style feedback, and rule-based checks apply word-count penalties plus writing analytics.

This is a portfolio demo, not an official IELTS scoring tool.

## Live demo

**Demo:** https://ai-ielts-writing-evaluator.onrender.com

Try it with:

- Username: `demo`
- Password: `demo123`

The first visit after idle time can take about a minute while the free server wakes up.

## What it does

- Generates IELTS Task 2 questions by topic
- Scores essays with a **TF-IDF + Random Forest** model trained on 1,435 labelled scripts
- Asks an LLM for band scores and feedback on the four official criteria
- Combines AI score, ML score, and word-count penalty into a final band
- Saves history, progress toward a target score, and a research comparison page

## Model results

| Model | MAE | RMSE | Exact | Within ±0.5 |
|---|---:|---:|---:|---:|
| **Random Forest** | **0.632** | **0.857** | 29.27% | **64.11%** |
| Linear Regression | 0.662 | 0.914 | 32.40% | 59.93% |
| Linear SVR | 0.697 | 0.921 | 25.78% | 59.58% |
| Ridge Regression | 0.716 | 0.920 | 21.25% | 59.23% |

Train / test split: 1,148 / 287.

## Architecture

```text
Browser  →  Flask + Flask-Login  →  SQLite
                              ├─ Random Forest band predictor
                              ├─ Groq LLM examiner feedback
                              └─ Writing analytics (vocab, cohesion, repeats)
```

Local development can still use [Ollama](https://ollama.com) if `GROQ_API_KEY` is not set.

## Tech stack

Flask, Flask-Login, scikit-learn, SQLite, Groq API, HTML/CSS/JS.

## Run locally

1. Create a virtualenv and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and add a free Groq key from [console.groq.com](https://console.groq.com/keys):

```bash
cp .env.example .env
```

3. Train the scoring model (needed once):

```bash
python train_model.py
```

4. Start the app:

```bash
python app.py
```

Open [http://127.0.0.1:5001](http://127.0.0.1:5001). Without a Groq key, the app falls back to local Ollama (`gemma3:1b`).

## Deploy free on Render

1. Push this repo to GitHub (public is best for a portfolio).
2. Get a Groq API key (free, no card required).
3. Go to [render.com](https://dashboard.render.com) → **New** → **Web Service** → connect the GitHub repo.
4. Use these settings:

   - **Runtime:** Python
   - **Build command:** `pip install -r requirements.txt && python train_model.py`
   - **Start command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 180`
   - **Instance type:** Free

5. Add environment variables:

   | Key | Value |
   |---|---|
   | `SECRET_KEY` | any long random string |
   | `GROQ_API_KEY` | your Groq key |
   | `GROQ_MODEL` | `openai/gpt-oss-20b` |

6. Deploy. Render gives you an `https://….onrender.com` URL. Put that URL in this README, GitHub About, LinkedIn, and your CV.

SQLite on the free plan is wiped when the service restarts. That is fine for a demo.

## Project layout

```text
app.py                      Flask app (auth, evaluate, history, progress)
train_model.py              Trains and compares scoring models
generate_research_metrics.py  Writes model_metrics.json
dataset/                    Labelled IELTS writing scripts
templates/  static/         UI
```

The large `ielts_question_generator` weights are local-only and are not required to run the web app.

## Portfolio blurb

> Built an IELTS Writing evaluator that combines a Random Forest model (MAE 0.63 on 1,435 essays) with LLM examiner feedback, user accounts, and progress tracking. Deployed as a Flask app with a public demo.
