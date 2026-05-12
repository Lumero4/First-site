import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai 

app = Flask(__name__)
CORS(app)

# API Key configuration
API_KEY = "AIzaSyBtl-Wh7ifJcGpYNlYl9M8rPf56yU_zOE8" 
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.0-flash" 

# Absolute path for the DB ensures it persists correctly on Render
DB_FILE = os.path.join(os.getcwd(), 'users_db.json')

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            try: 
                return json.load(f)
            except: 
                return {"users": {}}
    return {"users": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    if not username:
        return jsonify({"error": "Username required"}), 400
    
    db = load_db()
    if username in db['users']:
        return jsonify({"error": "User already exists"}), 400
    
    # Initialize new user with 0 XP
    db['users'][username] = {
        "xp": 0,
        "history": []
    }
    save_db(db)
    return jsonify({"status": "success", "xp": 0})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    db = load_db()
    
    if username not in db['users']:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "status": "success", 
        "xp": db['users'][username].get('xp', 0)
    })

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
    username = data.get('username')
    gain = data.get('xp_gain', 0)
    
    db = load_db()
    if username in db['users']:
        db['users'][username]['xp'] += gain
        save_db(db)
        return jsonify({"status": "success", "total_xp": db['users'][username]['xp']})
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    # Port configuration for Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
