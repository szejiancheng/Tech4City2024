from flask import Flask, jsonify, request
# from flask_cors import CORS
import sqlite3


app = Flask(__name__) 
# CORS(app)

DATABASE = 'backend/database.db'

#Function stubs:
def perform_ai_processing(data):
    # Perform AI processing on the input data

    # Returns json with predicted classes and respective confidence scores
    return {'result': 'AI processing result'}

# Store the input and result in the database
def store_in_database(data, result):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Store image data in Images table
    cursor.execute(f'''
        INSERT INTO Images (filepath) VALUES {data}
    ''')
    connection.commit()
    image_id = cursor.lastrowid

    # Store inference data in Results table
    rows = []
    for pred in result['result']:
        rows.append((image_id, pred['label_id'], pred['confidence_score']))
    cursor.executemany(f'''
        INSERT INTO Results (image_id, label_id, confidence_score) VALUES (?, ?, ?)
    ''', rows)
    result_id = cursor.lastrowid

    return image_id, result_id

def fetch_all_results():
    # Fetch all results from the database
    return [{'input': 'input1', 'result': 'result1'}, {'input': 'input2', 'result': 'result2'}]


@app.route('/infer', methods=['POST'])
# POST /analyze: Accepts user input, performs AI processing, stores the input and result in the database, and returns the result.
def infer():
    # Access the raw data (file path) from the request
    data = request.data
    # Check if data is present
    if not data:
        # Return error response if no data is found
        return jsonify({'error': 'No image found'}), 400

    # Perform AI processing on the input data
    result = perform_ai_processing(data)

    # Store the input and result in the database
    image_id, result_id = store_in_database(data, result)
    if not (image_id and result_id):
        return jsonify({'error': 'failed to add data to database'}), 400

    # Return the result
    return jsonify(result), 200

# GET /results: Retrieves all stored inputs and their results from the database.
@app.route('/results', methods=['GET'])  
def get_results():
    # Fetch all results from the database
    results = fetch_all_results()
    return jsonify(results), 200