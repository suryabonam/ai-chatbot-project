from dotenv import load_dotenv
load_dotenv()

from flask_cors import CORS
from flask import Flask, request, jsonify

import requests

from werkzeug.security import generate_password_hash, check_password_hash

from db_utils import (
    find_answer_in_knowledge_base,
    save_message,
    get_db_connection
)

app = Flask(__name__)
CORS(app)

# ---------------- CHAT ROUTE ---------------- #

@app.route('/chat', methods=['POST'])
def chat():

    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({'error': 'Missing "message" in JSON body'}), 400

    user_message = data['message']

    # Search in database
    answer = find_answer_in_knowledge_base(user_message)

    # If not found -> ask Ollama
    if not answer:

        ollama_prompt = f"""
        You are an aquaculture chatbot.

        Rules:
        1. Answer only aquaculture and fish farming questions.
        2. Keep answers short and simple.
        3. Never generate Chinese or other languages.
        4. Never generate extra instructions.
        5. If the question is NOT related to aquaculture or fish farming,
        ALWAYS reply with EXACTLY this sentence and nothing else:
        "I am an aquaculture specialist so ask me aquaculture related questions."

        User question:
        {user_message}
        """

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": ollama_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            }
        )

        result = response.json()
        answer = result["response"]

    # Save conversation
    save_message(user_message, answer)

    return jsonify({'response': answer}), 200


# ---------------- SIGNUP ROUTE ---------------- #

@app.route('/signup', methods=['POST'])
def signup():

    data = request.get_json()

    username = data['username']
    email = data['email']
    password = data['password']

    # Hash password
    hashed_password = generate_password_hash(password)

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check existing email
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (email,))

    existing_user = cursor.fetchone()

    if existing_user:

        cursor.close()
        connection.close()

        return jsonify({
            'message': 'Email already exists'
        }), 400

    # Insert user
    insert_query = """
    INSERT INTO users (username, email, password)
    VALUES (%s, %s, %s)
    """

    values = (username, email, hashed_password)

    cursor.execute(insert_query, values)

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        'message': 'User registered successfully'
    }), 201


# ---------------- LOGIN ROUTE ---------------- #

@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data['email']
    password = data['password']

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE email = %s"

    cursor.execute(query, (email,))

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user and check_password_hash(user['password'], password):

        return jsonify({
            'message': 'Login successful'
        }), 200

    return jsonify({
        'message': 'Invalid email or password'
    }), 401


if __name__ == '__main__':
    app.run(debug=True, port=5000)