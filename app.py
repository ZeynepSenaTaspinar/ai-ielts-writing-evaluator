from flask import Flask, request, jsonify, render_template, redirect, url_for
from openai import OpenAI
import joblib
import sqlite3
import re
import random
import json


from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "secret123"

client = OpenAI(api_key="YOURAPIKEEY")
ml_model = joblib.load("ielts_score_model.pkl")
TOPICS = {
    "education": [
        ("students should focus on academic subjects", "students should learn practical life skills"),
        ("children should start school at an early age", "children should begin formal education later"),
        ("homework is necessary for students", "homework creates unnecessary pressure")
    ],

    "technology": [
        ("technology improves the quality of education", "technology distracts students from learning"),
        ("artificial intelligence will create more jobs", "artificial intelligence will replace many workers"),
        ("social media helps people communicate", "social media harms real relationships")
    ],

    "environment": [
        ("governments should be responsible for protecting the environment", "individuals should take responsibility"),
        ("economic growth is more important than environmental protection", "environmental protection should be the priority"),
        ("public transport should be free", "people should pay for the transport they use")
    ],

    "work": [
        ("working from home is more effective", "working in an office is better for productivity"),
        ("salary is the most important factor in choosing a job", "job satisfaction is more important than salary"),
        ("people should stay in one career for life", "people should change careers when necessary")
    ],

    "health": [
        ("governments should regulate unhealthy food", "people should be free to choose what they eat"),
        ("public health is mainly the responsibility of governments", "individuals are responsible for their own health"),
        ("sports should be compulsory in schools", "students should choose whether to do sports")
    ]
}

QUESTION_TYPES = [
    "Discuss both views and give your own opinion.",
    "To what extent do you agree or disagree?",
    "What are the advantages and disadvantages?"
]

def get_db():
    return sqlite3.connect("database.db")


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        target_score REAL DEFAULT 7.0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question TEXT,
        essay TEXT,
        ai_score REAL,
        ml_score REAL,
        final_score REAL,
        ai_feedback TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route("/")
@login_required
def home():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT username, target_score
        FROM users
        WHERE id=?
    """, (current_user.id,))

    user = c.fetchone()
    conn.close()

    return render_template("index.html", user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO users (username, password, target_score) VALUES (?, ?, ?)",
                (username, password, 7.0)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            conn.close()
            return "User already exists"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            login_user(User(user[0]))
            return redirect(url_for("home"))

        return "Invalid username or password"

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    conn = get_db()
    c = conn.cursor()

    if request.method == "POST":
        target_score = float(request.form["target_score"])

        c.execute("""
            UPDATE users
            SET target_score=?
            WHERE id=?
        """, (target_score, current_user.id))

        conn.commit()
        conn.close()

        return redirect(url_for("progress"))

    c.execute("""
        SELECT username, target_score
        FROM users
        WHERE id=?
    """, (current_user.id,))

    user = c.fetchone()
    conn.close()

    return render_template("profile.html", user=user)


@app.route("/history")
@login_required
def history():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT id, question, ai_score, ml_score, final_score
        FROM evaluations
        WHERE user_id=?
        ORDER BY id DESC
    """, (current_user.id,))

    data = c.fetchall()
    conn.close()

    return render_template("history.html", data=data)


@app.route("/evaluation/<int:evaluation_id>")
@login_required
def evaluation_detail(evaluation_id):
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT question, essay, ai_score, ml_score, final_score, ai_feedback
        FROM evaluations
        WHERE id=? AND user_id=?
    """, (evaluation_id, current_user.id))

    item = c.fetchone()
    conn.close()

    if not item:
        return "Evaluation not found"

    return render_template("evaluation_detail.html", item=item)


@app.route("/progress")
@login_required
def progress():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT target_score
        FROM users
        WHERE id=?
    """, (current_user.id,))

    target_row = c.fetchone()
    target_score = target_row[0] if target_row and target_row[0] else 7.0

    c.execute("""
        SELECT final_score
        FROM evaluations
        WHERE user_id=?
        ORDER BY id ASC
    """, (current_user.id,))

    scores = [row[0] for row in c.fetchall()]
    conn.close()

    total = len(scores)
    average = round(sum(scores) / total, 2) if total else 0
    best = max(scores) if scores else 0

    if total == 0:
        progress_message = "No essays evaluated yet."
        trend_message = "No trend available yet."
        trend_class = "neutral-trend"
    elif total == 1:
        progress_message = f"Your first recorded score is {scores[-1]}."
        trend_message = "Complete more essays to see your progress trend."
        trend_class = "neutral-trend"
    else:
        previous_score = scores[-2]
        latest_score = scores[-1]
        change = round(latest_score - previous_score, 2)

        if change > 0:
            progress_message = f"You improved from {previous_score} to {latest_score}."
            trend_message = f"↑ Improved by +{change} band."
            trend_class = "positive-trend"
        elif change < 0:
            progress_message = f"Your score changed from {previous_score} to {latest_score}."
            trend_message = f"↓ Decreased by {abs(change)} band."
            trend_class = "negative-trend"
        else:
            progress_message = f"Your latest score stayed the same at {latest_score}."
            trend_message = "→ No change from the previous essay."
            trend_class = "neutral-trend"

    return render_template(
        "progress.html",
        total=total,
        average=average,
        best=best,
        scores=scores,
        progress_message=progress_message,
        trend_message=trend_message,
        trend_class=trend_class,
        target_score=target_score
    )

@app.route("/research")
@login_required
def research():
    with open("model_metrics.json", "r") as f:
        metrics = json.load(f)

    return render_template("research.html", metrics=metrics)   

@app.route("/suggest-question")
@login_required
def suggest_question():

    topic = random.choice(list(TOPICS.keys()))
    idea_a, idea_b = random.choice(TOPICS[topic])
    q_type = random.choice(QUESTION_TYPES)

    if "Discuss both views" in q_type:
        question = (
            f"Some people believe that {idea_a}, "
            f"while others think that {idea_b}. "
            f"{q_type}"
        )

    elif "agree or disagree" in q_type:
        question = (
            f"Some people believe that {idea_a}. "
            f"{q_type}"
        )

    else:
        question = (
            f"In many countries, more people believe that {idea_a}. "
            f"{q_type}"
        )

    return jsonify({
        "question": question
    })

def analyze_writing(essay):
    words = re.findall(r"\b\w+\b", essay.lower())
    sentences = re.split(r"[.!?]+", essay)
    sentences = [s.strip() for s in sentences if s.strip()]
    paragraphs = [p.strip() for p in essay.split("\n") if p.strip()]

    total_words = len(words)
    unique_words = len(set(words))
    vocabulary_diversity = round(unique_words / total_words, 2) if total_words else 0

    avg_sentence_length = round(total_words / len(sentences), 1) if sentences else 0

    transition_words = [
        "however", "therefore", "moreover", "furthermore", "although",
        "because", "for example", "for instance", "in conclusion",
        "on the other hand", "in addition", "as a result"
    ]

    transition_count = sum(essay.lower().count(t) for t in transition_words)

    repeated_words = {}
    for word in words:
        if len(word) > 4:
            repeated_words[word] = repeated_words.get(word, 0) + 1

    repeated_words = {
        k: v for k, v in repeated_words.items()
        if v >= 3
    }

    top_repeated = sorted(
        repeated_words.items(),
        key=lambda x: x[1],
        reverse=True
    )[:8]

    return {
        "vocabulary_diversity": vocabulary_diversity,
        "average_sentence_length": avg_sentence_length,
        "paragraph_count": len(paragraphs),
        "transition_words_count": transition_count,
        "top_repeated_words": top_repeated
    }
@app.route("/evaluate", methods=["POST"])
@login_required
def evaluate():
    try:
        data = request.get_json(force=True)
        question = data.get("question", "").strip()
        essay = data.get("essay", "").strip()

        if not question:
            return jsonify({"error": "No question provided"}), 400

        if not essay:
            return jsonify({"error": "No essay provided"}), 400

        word_count = len(essay.split())
        writing_analytics = analyze_writing(essay)

        if word_count < 200:
            word_penalty = 1.0
        elif word_count < 250:
            word_penalty = 0.5
        else:
            word_penalty = 0.0

        ml_input = question + "\n\n" + essay
        ml_score = ml_model.predict([ml_input])[0]
        ml_score = round(ml_score * 2) / 2

        prompt = f"""
You are a strict IELTS Academic Writing Task 2 examiner.

Evaluate the student's essay according to IELTS Writing Task 2 criteria.

Dataset-trained ML predicted overall band score:
{ml_score}

Exact Word Count: {word_count}
Word Count Penalty Applied: {word_penalty}

Use this ML score as an additional reference, but still evaluate the essay independently.

Use these criteria:
1. Task Response
2. Coherence and Cohesion
3. Lexical Resource
4. Grammatical Range and Accuracy

Be strict and realistic.
Penalize essays under 250 words using the provided word count penalty.
Do not give high scores easily.
Focus on whether the essay answers the specific question.

Return your answer exactly in this format:

Overall Band Score: [score]
ML Predicted Band Score: {ml_score}
Exact Word Count: {word_count}
Word Count Penalty Applied: {word_penalty}

Task Response: [band]
[feedback]

Coherence and Cohesion: [band]
[feedback]

Lexical Resource: [band]
[feedback]

Grammatical Range and Accuracy: [band]
[feedback]

Main Strengths:
- [point 1]
- [point 2]
- [point 3]

Main Improvements Needed:
- [point 1]
- [point 2]
- [point 3]

Improved Version:
[Write an improved version of the essay.]

IELTS Task 2 Question:
{question}

Student Essay:
{essay}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict professional IELTS Writing Task 2 examiner."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = response.choices[0].message.content

        match = re.search(r"Overall Band Score:\s*([0-9](?:\.[0-9])?)", result)
        ai_score = float(match.group(1)) if match else 0.0

        raw_final_score = round(((ai_score + ml_score) / 2) * 2) / 2
        final_score = max(0, raw_final_score - word_penalty)

        conn = get_db()
        c = conn.cursor()

        c.execute("""
            INSERT INTO evaluations (
                user_id,
                question,
                essay,
                ai_score,
                ml_score,
                final_score,
                ai_feedback
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            current_user.id,
            question,
            essay,
            ai_score,
            ml_score,
            final_score,
            result
        ))

        conn.commit()
        conn.close()

        return jsonify({
    "result": result,
    "ml_score": ml_score,
    "final_score": final_score,
    "word_count": word_count,
    "word_penalty": word_penalty,
    "writing_analytics": writing_analytics
})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
