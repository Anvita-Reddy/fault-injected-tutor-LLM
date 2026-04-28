# AI Tutor Chat App

A Flask-based chat application powered by Google Gemini. User info and full conversation history are saved to `users.json` for later review.

---

## Setup

### 1. Clone / download the project

Make sure your folder structure looks like this:

```
project/
├── app.py
├── requirements.txt
├── .env
└── templates/
    ├── login.html
    └── chat.html
```

---

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set up your `.env` file

Create a file named `.env` in the root of the project (same folder as `app.py`):

```
GEMINI_API_KEY=your_api_key_here
```

**How to get a Gemini API key:**
1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API key**
4. Copy the key and paste it into your `.env` file

> ⚠️ Never commit your `.env` file to Git. Add it to `.gitignore`.

---

### 5. Run the app

```bash
python app.py
```

Then open your browser and go to:

```
http://127.0.0.1:5000
```

---

## How it works

1. User enters their **name and email** on the login page
2. They are redirected to the chat interface
3. Each message is sent to Gemini and the response is streamed back
4. Every message (user + AI) is saved to `users.json` with a timestamp
5. Logging out ends the session but **keeps the record** in `users.json`

---

## Reviewing user data

All sessions are stored in `users.json` in the project root. Example structure:

```json
{
  "a3f1c2d4-...": {
    "user_name": "Alex",
    "user_email": "alex@example.com",
    "joined_at": "2026-04-18T13:00:00",
    "chat_history": [
      { "role": "user",      "content": "How does backpropagation work?", "timestamp": "2026-04-18T13:01:00" },
      { "role": "assistant", "content": "Great question...",              "timestamp": "2026-04-18T13:01:02" }
    ]
  }
}
```

You can open the file in any text editor, or load it into Python for analysis:

```python
import json

with open("users.json") as f:
    data = json.load(f)

for session_id, user in data.items():
    print(user["user_name"], user["user_email"])
    for msg in user["chat_history"]:
        print(f"  [{msg['role']}] {msg['content']}")
```

---

## Notes

- The app runs in **debug mode** by default — do not use this in production
- Chat history is stored **in memory and in `users.json`** — restarting the server clears the in-memory session but the JSON file persists
- Python 3.10+ is recommended
