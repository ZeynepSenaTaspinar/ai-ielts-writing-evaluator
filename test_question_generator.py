import random

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
    "What are the advantages and disadvantages?",
    "What are the causes of this problem, and what solutions can you suggest?"
]

def generate_question():
    topic = random.choice(list(TOPICS.keys()))
    idea_a, idea_b = random.choice(TOPICS[topic])
    q_type = random.choice(QUESTION_TYPES)

    if "Discuss both views" in q_type:
        return (
            f"Some people believe that {idea_a}, while others think that {idea_b}. "
            f"{q_type}"
        )

    if "agree or disagree" in q_type:
        return (
            f"Some people believe that {idea_a}. "
            f"{q_type}"
        )

    if "advantages and disadvantages" in q_type:
        return (
           f"In many countries, more people believe that {idea_a}. "
           f"{q_type}"
    )

    return (
        f"In many societies, {idea_a} has become an important issue. "
        f"{q_type}"
    )

print("\n===== GENERATED QUESTION =====\n")
print(generate_question())
