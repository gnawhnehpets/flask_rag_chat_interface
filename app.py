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



# @app.route('/get_response', methods=['POST'])
# def get_response():
#     user_message = request.form['message']
#     api_url = os.getenv('API_URL')
#     headers = {
#         'accept': 'application/json',
#         'Content-Type': 'application/json'
#     }
#     # payload = {
#     #     "input": {
#     #         "input": user_message,
#     #         "chat_history": []
#     #     },
#     #     "config": {},
#     #     "kwargs": {}
#     # }

#     # Attach the session_id to the payload
#     session_id = session.get('session_id', 'unknown')
#     payload['input']['input'] = user_message
#     payload['session_id'] = session_id  # Add session_id to payload

#     print(payload)

#     unique_url = f"{api_url}"
#     # unique_url = f"{api_url}?_={int(time.time())}"

#     logging.debug(f"Payload being sent to API: {payload}")

#     try:
#         response = requests.post(unique_url, json=payload, headers=headers)
#         response.raise_for_status()  # Raise an HTTPError for bad responses

#         logging.debug(f"Response received: {response.text}")

#         # Check if the response content is JSON
#         if response.headers.get('Content-Type') == 'application/json':
#             response_json = response.json()
#             bot_response = response_json.get('output', 'Sorry, I did not understand that.')
#         else:
#             print(f"Unexpected content type: {response.headers.get('Content-Type')}")
#             logging.error(f"Unexpected content type: {response.headers.get('Content-Type')}")
#             bot_response = 'Sorry, the response from the server was not in JSON format.'

#         bot_response = add_hyperlink(bot_response)
#         bot_response = format_response(bot_response)  # Format response to replace newlines with <br>
#         payload['input']['chat_history'].append([user_message, bot_response])
#         print(payload)
#     except requests.exceptions.HTTPError as http_err:
#         logging.error(f"HTTP error occurred: {http_err}")
#         bot_response = 'Sorry, there was an error processing your request.'
#     except Exception as err:
#         logging.error(f"Other error occurred: {err}")
#         bot_response = 'Sorry, there was an error processing your request.'

#     return jsonify({'response': bot_response})

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form['message']
    api_url = os.getenv('API_URL')
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

    session_id = session.get('session_id', 'unknown')
    payload['input']['input'] = user_message
    payload['session_id'] = session_id

    try:
        # response = requests.post(api_url, json=payload, headers=headers)
        # response.raise_for_status()
        # response_json = response.json()
        response_json={
                            "output": {
                                "input": [
                                {
                                    "content": "what variables are there related to sickle cell?",
                                    "additional_kwargs": {},
                                    "response_metadata": {},
                                    "type": "human",
                                    "name": "user_question",
                                    "id": "user_question"
                                },
                                {
                                    "content": "• DAGESICK (phv00123321): 77 age dad diagnosed -  sickle cell disease \n(from phs000284)",
                                    "additional_kwargs": {},
                                    "response_metadata": {},
                                    "type": "ai",
                                    "name": "KG_lookup_agent",
                                    "id": None,
                                    "invalid_tool_calls": [],
                                    "extra_meta_data": {
                                    "knowledge_graph": {
                                        "nodes": [
                                        {
                                            "name": "Sickle Cell Trait",
                                            "category": [
                                            "biolink:ThingWithTaxon",
                                            "biolink:BiologicalEntity",
                                            "biolink:NamedThing",
                                            "biolink:Disease",
                                            "biolink:DiseaseOrPhenotypicFeature"
                                            ],
                                            "equivalent_identifiers": [
                                            "MEDDRA:10020021",
                                            "NCIT:C39800",
                                            "UMLS:C0037054",
                                            "MEDDRA:10040656",
                                            "MEDDRA:10040650",
                                            "MEDDRA:10055612",
                                            "SNOMEDCT:16402000",
                                            "MESH:D012805",
                                            "MEDDRA:10019174"
                                            ],
                                            "information_content": 85.5,
                                            "description": "An individual who is heterozygous for the mutation that causes sickle cell anemia.",
                                            "id": "UMLS:C0037054"
                                        },
                                        {
                                            "name": "DAGESICK",
                                            "category": [
                                            "biolink:StudyVariable"
                                            ],
                                            "description": "77 age dad diagnosed -  sickle cell disease",
                                            "id": "phv00123321.v1.p1"
                                        },
                                        {
                                            "category": [
                                            "biolink:Study"
                                            ],
                                            "name": "phs000284.v2.p1",
                                            "id": "phs000284.v2.p1"
                                        }
                                        ],
                                        "edges": [
                                        {
                                            "subject": "UMLS:C0037054",
                                            "predicate": "biolink:related_to",
                                            "predicate_label": "related to",
                                            "relation": "biolink:related_to",
                                            "relation_label": "related to",
                                            "object": "phv00123321.v1.p1",
                                            "provided_by": "renci.bdc.semanticsearch.annotator",
                                            "id": "b01acb3cc6297c65"
                                        },
                                        {
                                            "subject": "phv00123321.v1.p1",
                                            "predicate": "biolink:part_of",
                                            "predicate_label": "part of",
                                            "relation": "BFO:0000050",
                                            "relation_label": "part of",
                                            "object": "phs000284.v2.p1",
                                            "provided_by": "renci.bdc.semanticsearch.annotator",
                                            "id": "79c1fd76235547d3"
                                        }
                                        ]
                                    }
                                    },
                                    "tool_calls": [],
                                    "example": False,
                                    "usage_metadata": None
                                }
                                ],
                                "next": "KG_lookup",
                                "chat_history": []
                            },
                            "metadata": {
                                "run_id": "6de63e7e-eef5-489d-91f8-477f62f43fe4",
                                "feedback_tokens": []
                            }
                        }
        
        bot_response = response_json.get('output', {}).get('input', [{}])[-1].get('content', 'Sorry, I did not understand that.')
        knowledge_graph = response_json.get('output', {}).get('input', [{}])[-1].get('extra_meta_data', {}).get('knowledge_graph', {})
        
        # Return bot response and graph data
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