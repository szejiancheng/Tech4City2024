from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import base64

app = Flask(__name__) 
# CORS(app)

DATABASE = os.path.join(os.path.dirname(__file__), 'backend', 'database.db')
app.config['DATABASE'] = DATABASE

def init_db():
    if not os.path.exists(os.path.dirname(DATABASE)):
        os.makedirs(os.path.dirname(DATABASE))
    if not os.path.exists(DATABASE):
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Images (
                image_id INTEGER PRIMARY KEY,
                user_id TEXT NOT NULL,
                image_data BLOB NOT NULL,
                file_path TEXT NOT NULL,
                content_type TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Results (
                result_id INTEGER PRIMARY KEY,
                image_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                label TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                result_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                preferred INTEGER DEFAULT 0,
                FOREIGN KEY (image_id) REFERENCES Images (image_id)
            )
        ''')
        connection.commit()
        connection.close()

# Initialize the database
init_db()

# Perform AI processing on the input data
def perform_ai_processing(data):
    print('Performing AI inference...')

    # Returns json with predicted classes and respective confidence scores
    ## result = [list of {'label': str, 'confidence_score': float}]
    return [{'label': 'fish', 'confidence_score': '0.876'},
            {'label': 'chicken', 'confidence_score': '0.543'}]

# Store the input and result in the database
def store_in_database(data, result):
    print('Storing data in database...')

    try:
        connection = sqlite3.connect(app.config['DATABASE'])
        cursor = connection.cursor()

        # Extract data
        user_id, image_data, file_path, content_type = \
            data['user_id'], data['image_data'], data['file_path'], data['content_type']

        # Store image data in Images table
        cursor.execute('''
            INSERT INTO Images (user_id, image_data, file_path, content_type) VALUES (?, ?, ?, ?)
        ''', (user_id, image_data, file_path, content_type))
        connection.commit()
        image_id = cursor.lastrowid

        # Store inference data in Results table
        rows = []
        for pred in result:
            label, confidence_score = pred['label'], pred['confidence_score']
            rows.append((image_id, user_id, label, confidence_score))
        cursor.executemany('''
            INSERT INTO Results (image_id, user_id, label, confidence_score) VALUES (?, ?, ?, ?)
        ''', rows)
        connection.commit()
        result_id = cursor.lastrowid

        connection.close()
        print(f'Image added in database: {image_id} with result: {result_id}')

        return image_id, result_id
    except sqlite3.Error as e:
        print(f'SQLite error: {e}')
        return None, None


# Fetch results from the database
def fetch_results(user_id, image_id = None, selected = False):
    print(f'Fetching results for user {user_id}...')

    connection = sqlite3.connect(app.config['DATABASE'])
    cursor = connection.cursor()

    # Retrieve data from db. If necessary, filter for specific image or only verified results
    sql = f'''
        SELECT * FROM Results WHERE user_id = "{user_id}" 
    '''
    if image_id:
        sql += f'''
            AND image_id = {image_id}
        '''
    if selected:
        sql += f'''
            AND preferred = 1
        '''
    # print(sql)
    cursor.execute(sql)
    results = cursor.fetchall()

    if not results:
        print(f'No results found!')

    connection.close()

    # Process table into output
    ret_output = []
    if results:
        for result in results:
            (curr_result_id, curr_user_id, curr_image_id, curr_label, \
             curr_confidence_score, curr_result_timestamp, _) = result
            ret_output.append({
                'result_id': curr_result_id,
                'user_id': curr_user_id,
                'image_id': curr_image_id,
                'label_name': curr_label,
                'confidence_score': curr_confidence_score,
                'result_timestamp': curr_result_timestamp 
            })

    return ret_output

# Updates database to indicate result preferred by user
def set_preference(result_id):
    success = True
    connection = sqlite3.connect(app.config['DATABASE'])
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

    connection = sqlite3.connect(app.config['DATABASE'])
    cursor = connection.cursor()

    # Placeholder string for the SQL query, ie (?, ?, ?) of the correct length
    placeholder = ','.join(['?' for _ in range(len(image_id_lst))])

    # Fetch rows from Images table
    cursor.execute(f'''
        SELECT * FROM Images WHERE user_id = "{user_id}" AND image_id IN ({placeholder})
    ''', image_id_lst)
    rows = cursor.fetchall()
    connection.close()

    # Create image objects
    for row in rows:
        (curr_image_id, curr_user_id, curr_image_data, curr_file_path, curr_content_type, curr_upload_date) = row
        # Convert data to string so that they can be encoded
        curr_obj = {
            'image_id': curr_image_id,
            'user_id': curr_user_id,
            'image_data': base64.b64encode(curr_image_data).decode('utf-8'),
            'upload_date': curr_upload_date
        }

        # Create multipart response using encoder
        # ret_images[curr_image_id] = MultipartEncoder(fields=curr_obj)
        ret_images[curr_image_id] = curr_obj

    return ret_images

# Check if user exists
def check_user(user_id):
    connection = sqlite3.connect(app.config['DATABASE'])
    cursor = connection.cursor()

    cursor.execute(f'''
        SELECT * FROM Images WHERE user_id = "{user_id}"
    ''')
    row = cursor.fetchone()
    connection.close()

    return True if row else False


# GET /results: Retrieves (preferred) results of user's uploaded images from the database.
@app.route('/results/<user_id>', methods=['GET'])  
def get_results(user_id):
    print('Fetching results...')

    # Check if user exists
    if not check_user(user_id):
        return jsonify({'error': 'No such user'}), 400

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

    # Output should not be jsonify-ied as it is a multipart response
    return jsonify(ret_output), 200

@app.route('/analyze', methods=['POST'])
# POST /analyze: Accepts user input, performs AI processing, stores the input and result in the database, and returns the result.
def analyze():
    print('Analyzing...')

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
    image_id, result_id = store_in_database(data, result)
    if image_id is None or result_id is None:
        return jsonify({'error': 'failed to add data to database'}), 400

    # Generate list of result_obj
    results_lst = fetch_results(user_id, image_id)

    # Return the result
    return jsonify(results_lst), 200

# POST /select: Accepts result that is preferred by user and updates database accordingly
@app.route('/select', methods=['POST'])  
def select():
    print('Setting user preferrence...')
    data = request.get_json()
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


if __name__ == '__main__':
    app.run(debug=True, port=8000)
