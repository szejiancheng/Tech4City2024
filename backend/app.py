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

    connection.close()

    return image_id, result_id


# Fetch results from the database
def fetch_results(filepath = None):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Join tables, filtering if necessary
    sql = '''
        SELECT 
            Images.upload_date, 
            Labels.label_name, 
            Results.confidence_score
        FROM 
            Images
        JOIN 
            Results ON Images.image_id = Results.image_id
        JOIN 
            Labels ON Results.label_id = Labels.label_id
    '''
    if filepath:
        sql += f'''
            WHERE Images.filepath = {filepath}
        '''
    cursor.execute(sql)
    results = cursor.fetchall()
    connection.close()

    # Process table into output
    ret_output = {}
    if results:
        for result in results:
            if result['filepath'] not in ret_output:
                ret_output[result['filepath']] = {
                    'timestamp': result['upload_date'],
                    'predictions': []
                }
            else:
                ret_output[result['filepath']]['predictions'].append({
                    'label_name': result['label_name'],
                    'confidence_score': result['confidence_score']
                })

    return ret_output


@app.route('/analyze', methods=['POST'])
# POST /analyze: Accepts user input, performs AI processing, stores the input and result in the database, and returns the result.
def analyze():
    # Access the raw data (file path) from the request
    data = request.data
    # Check if data is present
    if not data:
        # Return error response if no data is found
        return jsonify({'error': 'No image found'}), 400

    # Perform AI processing on the input data
    result = perform_ai_processing(data)
    if not result:
        return jsonify({'error': 'failed to make inference'}), 400

    # Store the input and result in the database
    image_id, result_id = store_in_database(data, result)
    if not (image_id and result_id):
        return jsonify({'error': 'failed to add data to database'}), 400

    # Return the result
    return jsonify(result), 200

# GET /results: Retrieves all stored inputs and their results from the database.
@app.route('/results', methods=['GET'])  
def get_all_results():
    # Fetch all results from the database
    results = fetch_results()
    return jsonify(results), 200


# GET /results: Retrieves results of specified image from the database.
@app.route('/results/<filepath>', methods=['GET'])  
def get_results(filepath):
    # Fetch relevant results from the database
    results = fetch_results(filepath)
    return jsonify(results), 200