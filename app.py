from flask import Flask, render_template, request, jsonify, url_for, send_file, session
import requests
import logging
import time
import re
import os
import json
import uuid
from io import BytesIO
app = Flask(__name__)

logging.basicConfig(level=logging.WARNING)
app.secret_key = str(uuid.uuid4())  # Needed to use sessions

# instantiate payload
payload = {
        "input": {
            "input": "",
            "chat_history": []
        },
        "config": {},
        "kwargs": {}
    }

def generate_session_id():
    return str(uuid.uuid4())

@app.route('/')
def home():
    # Generate a new session_id if not already in session
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())  # Generate a random session_id
        logging.debug(f"New session_id created: {session['session_id']}")
    else:
        logging.debug(f"Existing session_id: {session['session_id']}")

    # Clear the chat history whenever the home page is accessed
    payload['input']['chat_history'] = []
    
    banner_image_url = url_for('static', filename='images/banner.png')  # Example static image
    return render_template('index.html', banner_image_url=banner_image_url)
    # return render_template('index.html')

def add_hyperlink(text):
    # Regex to find standalone phs ID (e.g., phs123456) not part of a URL
    phs_pattern = r'\b(phs\d{4,})\b(?![^<]*<\/a>)'
    phs_replacement = r'<a href="https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=\1" target="_blank">\1</a>'

    # Regex to find URLs
    url_pattern = r'(https?://[^\s]+)'
    url_replacement = r'<a href="\1">\1</a>'

    # First, replace URLs with hyperlinks
    text = re.sub(url_pattern, url_replacement, text)

    # Then, replace standalone phs IDs with hyperlinks
    text = re.sub(phs_pattern, phs_replacement, text, flags=re.IGNORECASE)

    return text

def format_response(text):
    # Replace newlines with <br> tags
    text = text.replace('**', '')
    return text.replace('\n', '<br>')


@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form['message']
    api_url = os.getenv('API_URL')
    api_url_kg = os.getenv('API_URL_KG')
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

    session_id = session.get('session_id', 'unknown')
    payload['input']['input'] = user_message
    payload['session_id'] = session_id

    try:
        # RAG endpoint
        print("*** RAG ***")
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        print(json.dumps(response_json, indent=2))

        # KG endpoint
        print("*** KG response ***")
        print(api_url_kg)
        print(payload)
        print(headers)
        
        response_kg = requests.post(api_url_kg, json=payload, headers=headers)
        response_kg.raise_for_status()
        response_json_kg = response_kg.json()
        print(json.dumps(response_json_kg, indent=2))

        print("*** KG graph***")

        # Extract bot response
        output = response_json.get('output', {})
        if isinstance(output, str):
            bot_response = output  # Direct string response
        elif isinstance(output, dict):
            bot_response = output.get('input', [{}])[-1].get('content', 'Sorry, I did not understand that.')
        else:
            bot_response = 'Unexpected output format.'

        # Extract knowledge graph
        knowledge_graph = response_json_kg.get('output', {}).get('extra', {}).get('knowledge_graph', {})

        return jsonify({
            'response': bot_response,
            'knowledge_graph': knowledge_graph
        })
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return jsonify({'response': 'An error occurred while processing your request.'})

@app.route('/export_chat_history')
def export_chat_history():
    chat_history_json = json.dumps(payload['input']['chat_history'], indent=4)
    chat_history_bytes = BytesIO(chat_history_json.encode('utf-8'))
    chat_history_bytes.seek(0)

    return send_file(chat_history_bytes,
                     mimetype='application/json',
                     as_attachment=True,
                     download_name='chat_history.json')

@app.route('/clear_history', methods=['POST'])
def clear_history():
    # Clear the chat history in the payload
    payload['input']['chat_history'] = []
    return jsonify({'status': 'success', 'message': 'Chat history cleared.'})

if __name__ == '__main__':
    app.run(debug=True)