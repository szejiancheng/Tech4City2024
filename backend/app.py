from flask import Flask, jsonify, request
# from flask_cors import CORS
import sqlite3
from requests_toolbelt.multipart import MultipartEncoder


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
    user_id, image_data, file_path, content_type = \
        data['user_id'], data['image_data'], data['file_path'], data['content_type']
    label, confidence_score = pred['label'], pred['confidence_score']

    # Store image data in Images table
    cursor.execute('''
        INSERT INTO Images (user_id, image_data, file_path, content_type) VALUES (?, ?, ?, ?)
    ''', (user_id, image_data, file_path, content_type))
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

# Get image objects from IDs
def get_images_by_id(user_id, image_id_lst):
    # Output format = {image_id: image_obj}
    ret_images = {}

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Placeholder string for the SQL query, ie (?, ?, ?) of the correct length
    placeholder = ','.join(['?' for _ in len(image_id_lst)])

    # Fetch rows from Images table
    cursor.execute(f'''
        SELECT * FROM Images WHERE user_id = {user_id} AND image_id IN ({placeholder})
    ''', image_id_lst)
    rows = cursor.fetchall()
    connection.close()

    # Create image objects
    for row in rows:
        (curr_image_id, curr_user_id, curr_image_data, curr_file_path, curr_content_type, curr_upload_date) = row
        curr_obj = {
            'image_id': curr_image_id,
            'user_id': curr_user_id,
            'image_data': (curr_file_path, curr_image_data, curr_content_type),
            'upload_date': curr_upload_date
        }

        # Create multipart response using encoder
        ret_images[curr_image_id] = MultipartEncoder(fields=curr_obj)

    return ret_images


# GET /results: Retrieves (preferred) results of user's uploaded images from the database.
@app.route('/results/<user_id>', methods=['GET'])  
def get_results(user_id):
    # Each output should be a {image: _, results: _} object
    ret_output = []

    # Fetch relevant results from the database
    results = fetch_results(user_id=user_id, selected=True)

    # Fetch relevant image data
    image_id_lst = [result['image_id'] for result in results]
    image_obj_dict = get_images_by_id(user_id, image_id_lst)

    # Generate output objects
    for result in results:
        curr_output = {
            'image': image_obj_dict[result['image_id']], 
            'result': result
        }
        ret_output.append(curr_output)

    # Sort in upload order (earliest -> latest)
    ret_output.sort(key=lambda obj: obj['image']['upload_date'])

    return ret_output, 200

@app.route('/analyze', methods=['POST'])
# POST /analyze: Accepts user input, performs AI processing, stores the input and result in the database, and returns the result.
def analyze():  
    # Check if data is present
    if 'file' not in request.files or 'user_id' not in request.form:
        return jsonify({'error': 'File and user ID are required'}), 400
    
    # Retrieve file and user_id
    file = request.files['file']
    user_id = request.form['user_id']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Perform AI processing on the input data
    result = perform_ai_processing(file)
    if not result:
        return jsonify({'error': 'failed to make inference'}), 400
    
    # Collate data to be stored in the database
    data = {
        'user_id': user_id,
        'image_data': file.read(),
        'file_path': file.filename,
        'content_type': file.content_type
    }

    # Store the input and result in the database
    ## data = {'user_id': str, 'image_data': binary str}
    ## result = [list of {'label': str, 'confidence_score': float}]
    image_id, result_id = store_in_database(data, result)
    if not (image_id and result_id):
        return jsonify({'error': 'failed to add data to database'}), 400
    
    # Generate list of result_obj
    results_lst = fetch_results(user_id, image_id)

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
