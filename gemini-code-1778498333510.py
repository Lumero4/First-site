import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai 

app = Flask(__name__)
CORS(app)

# Replace with your actual Gemini API Key
API_KEY = "AIzaSyBtl-Wh7ifJcGpYNlYl9M8rPf56yU_zOE8" 
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.0-flash" 
DB_FILE = 'users_db.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            try: return json.load(f)
            except: return {"users": {"Mbianda J.": {"xp": 850}}}
    return {"users": {"Mbianda J.": {"xp": 850}}}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    data = request.json
    exam = data.get('exam')
    subject = data.get('subject')
    topic = data.get('topic')

    prompt = f"""
    You are an expert tutor for the Cameroonian educational system (MINESEC/OBC/GCE Board).
    Generate a study session for:
    Exam: {exam}
    Subject: {subject}
    Topic: {topic}

    CONTEXTUAL RULES:
    1. For GCE (A/O Level), use English.
    2. For Baccalauréat, Probatoire, and BEPC, use French.
    3. For CAP, use French and focus on practical technical knowledge.
    4. Provide 1 concise explanation (3 sentences) and 3 multiple-choice questions.

    RESPONSE FORMAT: Return ONLY a valid JSON object.
    {{
        "explanation": "...",
        "questions": [
            {{"question": "...", "options": ["A", "B", "C", "D"], "answer": 0}}
        ]
    }}
    """

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return jsonify(json.loads(response.text))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-xp', methods=['POST'])
def update_xp():
    data = request.json
    username = data.get('username', 'Mbianda J.')
    gain = data.get('xp_gain', 0)
    
    db = load_db()
    if username not in db['users']:
        db['users'][username] = {"xp": 0}
    
    db['users'][username]['xp'] += gain
    save_db(db)
    return jsonify({"status": "success", "total_xp": db['users'][username]['xp']})

if __name__ == '__main__':
    app.run(debug=True, port=5000)