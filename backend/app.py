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
    ## result = [list of {'label': str, 'confidence_score': float}]
    return

# Store the input and result in the database
def store_in_database(data, result):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Extract data
    user_id, image_data = data['user_id'], data['image_data']
    label, confidence_score = pred['label'], pred['confidence_score']

    # Store image data in Images table
    cursor.execute('''
        INSERT INTO Images (user_id, image_data) VALUES (?, ?)
    ''', (user_id, image_data))
    connection.commit()
    image_id = cursor.lastrowid

    # Store inference data in Results table
    rows = []
    for pred in result:
        rows.append((image_id, user_id, label, confidence_score))
    cursor.executemany('''
        INSERT INTO Results (image_id, user_id, label, confidence_score) VALUES (?, ?, ?, ?)
    ''', rows)
    result_id = cursor.lastrowid

    connection.close()

    return image_id, result_id


# Fetch results from the database
def fetch_results(user_id, image_id = None, selected = False):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Retrieve data from db. If necessary, filter for specific image or only verified results
    sql = f'''
        SELECT * FROM Results WHERE user.id = {user_id} 
    '''
    if image_id:
        sql += f'''
            WHERE Results.image_id = {image_id}
        '''
    if selected:
        sql += f'''
            WHERE Results.selected = 1
        '''
    cursor.execute(sql)
    results = cursor.fetchall()
    connection.close()

    # Process table into output
    ret_output = []
    if results:
        for result in results:
            ret_output.append({
                'result_id': result['result_id'],
                'user_id': result['user_id'],
                'image_id': result['image_id'],
                'label_name': result['label'],
                'result_timestamp': result['result_date'] 
            })

    return ret_output

# Updates database to indicate result preferred by user
def set_preference(result_id):
    success = True
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Update table
    cursor.execute(f'''
        UPDATE Results SET preferred = 1 WHERE result_id = {result_id}
    ''')

    connection.commit()
    connection.close()

    return success


# GET /results: Retrieves (preferred) results of specified image from the database.
@app.route('/results/<user_id>', methods=['GET'])  
def get_results(user_id):
    # Fetch relevant results from the database
    results = fetch_results(user_id=user_id, selected=True)
    return jsonify(results), 200

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
    ## data = {'user_id': str, 'image_data': binary str}
    ## result = [list of {'label': str, 'confidence_score': float}]
    image_id, result_id = store_in_database(data, result)
    if not (image_id and result_id):
        return jsonify({'error': 'failed to add data to database'}), 400
    
    # Generate list of result_obj
    results_lst = fetch_results(user_id=data['user_id'], image_id=image_id)

    # Return the result
    return jsonify(results_lst), 200

# POST /select: Accepts result that is preferred by user and updates database accordingly
@app.route('/select', methods=['POST'])  
def select():
    data = request.data
    # Check if data is present
    if not data:
        # Return error response if no data is found
        return jsonify({'error': 'Missing data'}), 400
    
    # Retrieve data
    result_id = data['result_id']

    # Set preference
    success = set_preference(result_id)

    if not success:
        jsonify({'error': 'Invalid request'}), 400
    
    return jsonify({'message': 'Preference set successfully!'}), 200
