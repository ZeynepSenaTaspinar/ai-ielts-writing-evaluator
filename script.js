const essayBox = document.getElementById("essay");
const wordCountBox = document.getElementById("wordCount");
const wordStatusBox = document.getElementById("wordStatus");
const evaluateBtn = document.getElementById("evaluateBtn");
const errorBox = document.getElementById("errorBox");
const resultSection = document.getElementById("resultSection");

function updateWordCount() {
  const text = essayBox.value.trim();
  const count = text ? text.split(/\s+/).length : 0;

  wordCountBox.innerText = "Word Count: " + count;

  if (count < 250) {
    wordStatusBox.innerText = "Below 250 words";
    wordStatusBox.classList.remove("success");
    wordStatusBox.classList.add("warning");
  } else {
    wordStatusBox.innerText = "Meets minimum word count";
    wordStatusBox.classList.remove("warning");
    wordStatusBox.classList.add("success");
  }
}

essayBox.addEventListener("input", updateWordCount);
updateWordCount();

function clearAll() {
  document.getElementById("question").value = "";
  document.getElementById("essay").value = "";

  document.getElementById("overallBand").innerText = "-";
  document.getElementById("mlPredictedScore").innerText = "-";
  document.getElementById("finalScore").innerText = "-";
  document.getElementById("exactWordCount").innerText = "-";
  document.getElementById("wordPenalty").innerText = "-";
  document.getElementById("scoreDifference").innerText = "-";
  document.getElementById("confidenceLevel").innerText = "-";

  document.getElementById("aiComparisonScore").innerText = "-";
  document.getElementById("mlComparisonScore").innerText = "-";
  document.getElementById("finalComparisonScore").innerText = "-";
  document.getElementById("scoreInterpretation").innerText = "-";

  document.getElementById("taskResponseBand").innerText = "-";
  document.getElementById("coherenceBand").innerText = "-";
  document.getElementById("lexicalBand").innerText = "-";
  document.getElementById("grammarBand").innerText = "-";

  document.getElementById("taskResponseText").innerText = "-";
  document.getElementById("coherenceText").innerText = "-";
  document.getElementById("lexicalText").innerText = "-";
  document.getElementById("grammarText").innerText = "-";

  document.getElementById("improvedVersion").innerText = "-";
  document.getElementById("rawResult").innerText = "-";
  document.getElementById("strengthsList").innerHTML = "";
  document.getElementById("improvementsList").innerHTML = "";
  document.getElementById("vocabularyDiversity").innerText = "-";
document.getElementById("avgSentenceLength").innerText = "-";
document.getElementById("paragraphCount").innerText = "-";
document.getElementById("transitionCount").innerText = "-";
document.getElementById("repeatedWordsList").innerHTML = "";

  errorBox.classList.add("hidden");
  errorBox.innerText = "";
  resultSection.classList.add("hidden");

  updateWordCount();
}

function getBetween(text, start, endList) {
  const startIndex = text.indexOf(start);
  if (startIndex === -1) return "";

  const from = startIndex + start.length;
  let endIndex = text.length;

  for (const end of endList) {
    const i = text.indexOf(end, from);
    if (i !== -1 && i < endIndex) {
      endIndex = i;
    }
  }

  return text.slice(from, endIndex).trim();
}

function cleanBandAndText(section) {
  return section.replace(/^[0-9](\.[0-9])?\s*/, "").trim();
}

function extractBand(text, label) {
  const regex = new RegExp(
    label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\s*([0-9](\\.[0-9])?)"
  );
  const match = text.match(regex);
  return match ? match[1] : "-";
}

function extractList(section) {
  return section
    .split("\n")
    .map(line => line.trim())
    .filter(line => line.startsWith("-"))
    .map(line => line.replace(/^-+\s*/, "").trim());
}

function fillList(id, items) {
  const el = document.getElementById(id);
  el.innerHTML = "";

  if (!items.length) {
    const li = document.createElement("li");
    li.innerText = "-";
    el.appendChild(li);
    return;
  }

  items.forEach(item => {
    const li = document.createElement("li");
    li.innerText = item;
    el.appendChild(li);
  });
}

function parseResult(text) {
  const overallBand = extractBand(text, "Overall Band Score:");

  const taskSection = getBetween(text, "Task Response:", [
    "Coherence and Cohesion:",
    "Lexical Resource:",
    "Grammatical Range and Accuracy:",
    "Main Strengths:",
    "Main Improvements Needed:",
    "Improved Version:"
  ]);

  const coherenceSection = getBetween(text, "Coherence and Cohesion:", [
    "Lexical Resource:",
    "Grammatical Range and Accuracy:",
    "Main Strengths:",
    "Main Improvements Needed:",
    "Improved Version:"
  ]);

  const lexicalSection = getBetween(text, "Lexical Resource:", [
    "Grammatical Range and Accuracy:",
    "Main Strengths:",
    "Main Improvements Needed:",
    "Improved Version:"
  ]);

  const grammarSection = getBetween(text, "Grammatical Range and Accuracy:", [
    "Main Strengths:",
    "Main Improvements Needed:",
    "Improved Version:"
  ]);

  const strengthsSection = getBetween(text, "Main Strengths:", [
    "Main Improvements Needed:",
    "Improved Version:"
  ]);

  const improvementsSection = getBetween(text, "Main Improvements Needed:", [
    "Improved Version:"
  ]);

  const improvedVersion = getBetween(text, "Improved Version:", []);

  return {
    overallBand,
    taskBand: extractBand(text, "Task Response:"),
    coherenceBand: extractBand(text, "Coherence and Cohesion:"),
    lexicalBand: extractBand(text, "Lexical Resource:"),
    grammarBand: extractBand(text, "Grammatical Range and Accuracy:"),
    taskText: cleanBandAndText(taskSection),
    coherenceText: cleanBandAndText(coherenceSection),
    lexicalText: cleanBandAndText(lexicalSection),
    grammarText: cleanBandAndText(grammarSection),
    strengths: extractList(strengthsSection),
    improvements: extractList(improvementsSection),
    improvedVersion
  };
}

function formatScore(value) {
  const number = parseFloat(value);
  return isNaN(number) ? "-" : number.toFixed(1);
}

function formatPenalty(value) {
  const number = parseFloat(value);
  if (isNaN(number)) return "-";
  if (number === 0) return "No penalty";
  return "Applied: " + number.toFixed(1);
}

function updateHybridScores(aiScoreRaw, mlScoreRaw, finalScoreRaw) {
  const aiScore = parseFloat(aiScoreRaw);
  const mlScore = parseFloat(mlScoreRaw);
  const finalScore = parseFloat(finalScoreRaw);

  if (isNaN(aiScore) || isNaN(mlScore)) {
    document.getElementById("scoreDifference").innerText = "-";
    document.getElementById("confidenceLevel").innerText = "-";
    document.getElementById("finalComparisonScore").innerText = "-";
    document.getElementById("scoreInterpretation").innerText = "-";
    return;
  }

  const difference = Math.abs(aiScore - mlScore);

  document.getElementById("scoreDifference").innerText = difference.toFixed(1);

  if (!isNaN(finalScore)) {
    document.getElementById("finalScore").innerText = finalScore.toFixed(1);
    document.getElementById("finalComparisonScore").innerText = finalScore.toFixed(1);
  }

  if (difference <= 0.5) {
    document.getElementById("confidenceLevel").innerText = "High";
    document.getElementById("scoreInterpretation").innerText =
      "AI and ML scores are close. The prediction is relatively consistent.";
  } else if (difference <= 1.0) {
    document.getElementById("confidenceLevel").innerText = "Medium";
    document.getElementById("scoreInterpretation").innerText =
      "AI and ML scores show a moderate difference. The result should be interpreted carefully.";
  } else {
    document.getElementById("confidenceLevel").innerText = "Low";
    document.getElementById("scoreInterpretation").innerText =
      "AI and ML scores differ significantly. Human review would be recommended.";
  }
}

async function sendEssay() {
  const question = document.getElementById("question").value.trim();
  const essay = document.getElementById("essay").value.trim();

  errorBox.classList.add("hidden");
  errorBox.innerText = "";

  if (!question) {
    errorBox.innerText = "Please enter the IELTS Task 2 question.";
    errorBox.classList.remove("hidden");
    return;
  }

  if (!essay) {
    errorBox.innerText = "Please write the essay first.";
    errorBox.classList.remove("hidden");
    return;
  }

  evaluateBtn.disabled = true;
  evaluateBtn.innerText = "Evaluating...";

  try {
    const res = await fetch("/evaluate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question, essay })
    });

    const data = await res.json();

    if (!res.ok) {
      errorBox.innerText = "Error: " + (data.error || "Unknown server error");
      errorBox.classList.remove("hidden");
      return;
    }

    const parsed = parseResult(data.result || "");

    document.getElementById("overallBand").innerText = formatScore(parsed.overallBand);
    document.getElementById("mlPredictedScore").innerText = formatScore(data.ml_score);
    document.getElementById("finalScore").innerText = formatScore(data.final_score);

    document.getElementById("exactWordCount").innerText = data.word_count || "-";
    document.getElementById("wordPenalty").innerText = formatPenalty(data.word_penalty);

    document.getElementById("aiComparisonScore").innerText = formatScore(parsed.overallBand);
    document.getElementById("mlComparisonScore").innerText = formatScore(data.ml_score);
    document.getElementById("finalComparisonScore").innerText = formatScore(data.final_score);

    updateHybridScores(parsed.overallBand, data.ml_score, data.final_score);
    const analytics = data.writing_analytics || {};

document.getElementById("vocabularyDiversity").innerText =
  analytics.vocabulary_diversity ?? "-";

document.getElementById("avgSentenceLength").innerText =
  analytics.average_sentence_length ?? "-";

document.getElementById("paragraphCount").innerText =
  analytics.paragraph_count ?? "-";

document.getElementById("transitionCount").innerText =
  analytics.transition_words_count ?? "-";

const repeatedList = document.getElementById("repeatedWordsList");
repeatedList.innerHTML = "";

if (analytics.top_repeated_words && analytics.top_repeated_words.length) {
  analytics.top_repeated_words.forEach(item => {
    const li = document.createElement("li");
    li.innerText = item[0] + " — " + item[1] + " times";
    repeatedList.appendChild(li);
  });
} else {
  const li = document.createElement("li");
  li.innerText = "No major repeated words detected.";
  repeatedList.appendChild(li);
}

    document.getElementById("taskResponseBand").innerText = parsed.taskBand || "-";
    document.getElementById("coherenceBand").innerText = parsed.coherenceBand || "-";
    document.getElementById("lexicalBand").innerText = parsed.lexicalBand || "-";
    document.getElementById("grammarBand").innerText = parsed.grammarBand || "-";

    document.getElementById("taskResponseText").innerText = parsed.taskText || "-";
    document.getElementById("coherenceText").innerText = parsed.coherenceText || "-";
    document.getElementById("lexicalText").innerText = parsed.lexicalText || "-";
    document.getElementById("grammarText").innerText = parsed.grammarText || "-";

    document.getElementById("improvedVersion").innerText = parsed.improvedVersion || "-";
    document.getElementById("rawResult").innerText = data.result || "-";

    fillList("strengthsList", parsed.strengths);
    fillList("improvementsList", parsed.improvements);

    resultSection.classList.remove("hidden");
  } catch (err) {
    errorBox.innerText = "Fetch error: " + err.message;
    errorBox.classList.remove("hidden");
  } finally {
    evaluateBtn.disabled = false;
    evaluateBtn.innerText = "Evaluate";
  }
}
async function suggestQuestion() {

  const suggestBtn = document.getElementById("suggestBtn");
  const questionBox = document.getElementById("question");

  suggestBtn.disabled = true;
  suggestBtn.innerText = "Generating...";

  try {

    const res = await fetch("/suggest-question");
    const data = await res.json();

    questionBox.value = data.question;

  } catch (err) {

    errorBox.innerText =
      "Question generation failed: " + err.message;

    errorBox.classList.remove("hidden");

  } finally {

    suggestBtn.disabled = false;
    suggestBtn.innerText = "Suggest Question";
  }
}