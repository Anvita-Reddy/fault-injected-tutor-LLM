# Fault-Injected Tutor LLM (FILI)

A Flask-based research platform that studies how students interact with AI tutors when the AI is confidently wrong. Built for an NYU class research project on AI trust calibration and error detection in human–AI learning contexts.

**🔗 Live demo:** https://genai-project-z66h.onrender.com
**Team:** Anvita Inture, Muskaan Kumar, Sravika Linga. 

---

## The Question

AI tutoring tools are being adopted faster than researchers can study them. Standard assessments measure whether students get the right answer — not whether they thought independently to get there. A student who copies a confident AI error and a student who verified the correct answer look identical in outcome data.

**FILI is the instrument that tells them apart.**

## How it works

Participants take an 8-question machine learning quiz. Alongside each question, they have access to an AI tutor that has been deliberately compromised: every explanation it gives points toward a wrong answer, and it defends that framing under pushback.

The tutor uses a **hybrid fault-injection architecture**:

- **Canned fault delivery.** When the participant asks a direct question ("what's the answer?", "is it B?"), the app returns a pre-written wrong explanation from a structured fault bank — identical across all participants for clean experimental control.
- **Gemini-pinned conversational layer.** For follow-up questions and pushback ("doesn't that contradict X?"), the app calls the Gemini API with the wrong framing pinned in its system prompt, so the tutor maintains the incorrect position naturally across conversation turns.

This hybrid approach combines the experimental rigor of pre-written stimuli with the conversational realism of a live LLM — addressing a methodological gap in prior fault-injection studies.

## Behavioral Instrumentation

Every interaction is logged to Supabase with full granularity:

- **MCQ submissions** — answer, correctness, whether it matches the AI's wrong suggestion
- **Tutor interactions** — every user message, AI response, and routing path (`canned`, `hedged`, `gemini_pinned`)
- **Confidence manipulation** — Q2 and Q6 each have high-confidence and hedged variants, randomly assigned per participant, enabling within-subjects analysis of how AI confidence framing affects override behavior

Participants are linked to a follow-up Qualtrics survey via `participant_id`, allowing behavioral data to be joined with self-report measures.

## Stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python) |
| Database | Supabase (Postgres) |
| LLM | Google Gemini (gemini-2.5-flash) |
| Hosting | Render |
| Survey | Qualtrics (joined via participant_id) |

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Consent   │────▶│     Quiz     │────▶│    Debrief      │
│             │      │ (8 Q's, MCQ) │      │  + Survey link  │
└─────────────┘      └──────┬───────┘      └─────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   AI Tutor    │
                    │   (routed)    │
                    └───┬───────┬───┘
                        │       │
              ┌─────────▼─┐   ┌─▼──────────────┐
              │ Fault     │   │  Gemini API    │
              │ bank      │   │  (wrong frame  │
              │ (canned)  │   │   pinned)      │
              └───────────┘   └────────────────┘
                        │       │
                        ▼       ▼
                ┌─────────────────────┐
                │  Supabase logging   │
                │  (3 tables)         │
                └─────────────────────┘
```


## Local Setup

```bash
git clone https://github.com/Anvita-Reddy/fault-injected-tutor-LLM
cd fault-injected-tutor-LLM
pip install -r requirements.txt
```

Create a `.env` file:

```
GEMINI_API_KEY=...
SUPABASE_URL=...
SUPABASE_KEY=...
FLASK_SECRET_KEY=...
```

Provision the Supabase schema (`participants`, `quiz_responses`, `tutor_interactions`), then:

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

---

*Built April 2026 as a class research project. The tutor is intentionally and ethically deceptive — all participants are debriefed.*
