import os
import uuid
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai
from google.genai import types

from fault_bank import QUESTIONS, QUESTION_ORDER

load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Keywords that signal "give me the answer" — route these to the fault bank.
ANSWER_KEYWORDS = [
    "answer", "which option", "what's the answer", "what is the answer",
    "correct answer", "right answer", "which one", "a or b", "b or c",
    "c or d", "is it a", "is it b", "is it c", "is it d",
    "should i pick", "which letter", "what should i choose", "tell me the answer",
    "solve", "solution", "explain this", "help with this", "this question",
    "explain the question", "help me with this"
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_participant():
    """Return participant_id from session, or None."""
    return session.get("participant_id")


def assign_confidence_variants():
    """Randomly assign hedged/high for Q2 and Q6."""
    return {
        "q2": random.choice(["high", "hedged"]),
        "q6": random.choice(["high", "hedged"]),
    }


def get_ai_response_for_question(question_id, participant_variants):
    """Look up the pre-written wrong answer for a question."""
    q = QUESTIONS[question_id]
    if q.get("confidence_pair"):
        variant_key = "q2" if question_id == "Q2" else "q6"
        variant = participant_variants.get(variant_key, "high")
        if variant == "hedged":
            return q["ai_response_hedged"], "hedged"
        return q["ai_response_high"], "high"
    return q["ai_response"], "standard"


def looks_like_answer_request(message):
    """Check if the message is asking for the direct answer to the MCQ."""
    msg_lower = message.lower()
    return any(kw in msg_lower for kw in ANSWER_KEYWORDS)


def build_gemini_prompt(question_id, participant_variants):
    """Build a system prompt for Gemini that pins the wrong framing for the current question."""
    q = QUESTIONS[question_id]

    if q.get("confidence_pair"):
        variant_key = "q2" if question_id == "Q2" else "q6"
        variant = participant_variants.get(variant_key, "high")
        wrong_explanation = q["ai_response_hedged"] if variant == "hedged" else q["ai_response_high"]
    else:
        wrong_explanation = q["ai_response"]

    return f"""You are a tutor helping a student with a machine learning quiz question. Be conversational and helpful. Keep responses to 2-4 sentences unless asked for more detail.

THE CURRENT QUESTION IS:
{q["text"]}

YOUR POSITION ON THIS QUESTION (defend this framing consistently):
{wrong_explanation}

CRITICAL RULES:
- Defend the framing above as the correct understanding. If the student suggests a different interpretation, explain why your framing is the right one.
- Never name a specific multiple-choice letter (A, B, C, or D) as the answer. If asked "is it B?", redirect them to think about which option matches the explanation you've given.
- Stay consistent. If you've described the concept one way, don't reverse yourself later in the conversation.
- For genuinely off-topic questions (unrelated to the current quiz question), respond normally and helpfully.
- Be confident. Don't hedge unless the framing above is itself hedged."""


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    """Landing page → consent."""
    return render_template("consent.html")


@app.route("/consent", methods=["POST"])
def consent():
    """Participant agreed to consent. Collect name/email, assign condition, create participant row."""
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    if not (name and email):
        return redirect(url_for("index"))

    participant_id = str(uuid.uuid4())
    variants = assign_confidence_variants()

    supabase.table("participants").insert({
        "participant_id": participant_id,
        "user_name": name,
        "user_email": email,
        "q2_confidence_variant": variants["q2"],
        "q6_confidence_variant": variants["q6"],
    }).execute()

    session["participant_id"] = participant_id
    session["variants"] = variants
    session["current_q"] = 0  # index into QUESTION_ORDER

    return redirect(url_for("quiz"))


@app.route("/quiz", methods=["GET"])
def quiz():
    """Show the current question."""
    pid = get_participant()
    if not pid:
        return redirect(url_for("index"))

    current_q_idx = session.get("current_q", 0)
    if current_q_idx >= len(QUESTION_ORDER):
        return redirect(url_for("debrief"))

    qid = QUESTION_ORDER[current_q_idx]
    q = QUESTIONS[qid]

    return render_template(
        "quiz.html",
        question_id=qid,
        question_text=q["text"],
        options=q["options"],
        question_number=current_q_idx + 1,
        total_questions=len(QUESTION_ORDER),
    )


@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    """Record participant's MCQ submission, advance to next question."""
    pid = get_participant()
    if not pid:
        return jsonify({"error": "No participant session"}), 401

    data = request.get_json()
    qid = data.get("question_id")
    answer = data.get("answer")

    if qid not in QUESTIONS or answer not in ["A", "B", "C", "D"]:
        return jsonify({"error": "Invalid submission"}), 400

    q = QUESTIONS[qid]
    is_correct = (answer == q["correct"])
    matches_ai = (answer == q["ai_says"])

    supabase.table("quiz_responses").insert({
        "participant_id": pid,
        "question_id": qid,
        "submitted_answer": answer,
        "is_correct": is_correct,
        "matches_ai_answer": matches_ai,
    }).execute()

    session["current_q"] = session.get("current_q", 0) + 1

    return jsonify({"next_url": url_for("quiz")})


@app.route("/ask_tutor", methods=["POST"])
def ask_tutor():
    """Participant asks the tutor. Route to fault bank or Gemini-with-pinned-wrong-framing."""
    pid = get_participant()
    if not pid:
        return jsonify({"error": "No participant session"}), 401

    data = request.get_json()
    user_message = data.get("message", "").strip()
    qid = data.get("question_id")

    if qid not in QUESTIONS:
        return jsonify({"error": "Invalid question"}), 400

    variants = session.get("variants", {})

    if looks_like_answer_request(user_message):
        # Direct answer request → return canned fault explanation verbatim
        ai_response, response_type = get_ai_response_for_question(qid, variants)
    else:
        # Conversational follow-up → Gemini, pinned to the wrong framing
        try:
            system_prompt = build_gemini_prompt(qid, variants)
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Content(role="user", parts=[types.Part(text=user_message)])],
                config=types.GenerateContentConfig(system_instruction=system_prompt)
            )
            ai_response = response.text
            response_type = "gemini_pinned"
        except Exception as e:
            print(f"GEMINI ERROR: {e}")
            ai_response = "Sorry, I had trouble responding. Could you rephrase?"
            response_type = "gemini_error"

    supabase.table("tutor_interactions").insert({
        "participant_id": pid,
        "question_id": qid,
        "user_message": user_message,
        "ai_response": ai_response,
        "ai_response_type": response_type,
    }).execute()

    return jsonify({"reply": ai_response})


@app.route("/debrief", methods=["GET"])
def debrief():
    """End screen — thanks + Qualtrics survey link with participant_id."""
    pid = get_participant()
    if not pid:
        return redirect(url_for("index"))
    return render_template("debrief.html", participant_id=pid)


@app.route("/reset")
def reset():
    """Clear session — useful for testing."""
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)