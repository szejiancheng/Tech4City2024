from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import base64

app = Flask(__name__)
CORS(app)

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

def perform_ai_processing(data):
    print('Performing AI inference...')
    return [{'label': 'fish', 'confidence_score': '0.876'},
            {'label': 'chicken', 'confidence_score': '0.543'}]

def store_in_database(data, result):
    print('Storing data in database...')
    try:
        connection = sqlite3.connect(app.config['DATABASE'])
        cursor = connection.cursor()

        user_id, image_data, file_path, content_type = data['user_id'], data['image_data'], data['file_path'], data['content_type']

        cursor.execute('''
            INSERT INTO Images (user_id, image_data, file_path, content_type) VALUES (?, ?, ?, ?)
        ''', (user_id, image_data, file_path, content_type))
        connection.commit()
        image_id = cursor.lastrowid

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

def fetch_results(user_id, image_id=None, selected=False):
    print(f'Fetching results for user {user_id}...')
    try:
        connection = sqlite3.connect(app.config['DATABASE'])
        cursor = connection.cursor()
        sql = f'SELECT * FROM Results WHERE user_id = "{user_id}"'
        if image_id:
            sql += f' AND image_id = {image_id}'
        if selected:
            sql += ' AND preferred = 1'
        
        cursor.execute(sql)
        results = cursor.fetchall()
        connection.close()

        if not results:
            print(f'No results found for user {user_id}.')
        

        ret_output = []
        if results:
            for result in results:
                (curr_result_id, curr_user_id, curr_image_id, curr_label, 
                 curr_confidence_score, curr_result_timestamp, _) = result
                ret_output.append({
                    'result_id': curr_result_id,
                    'image_id': curr_image_id,
                    'user_id': curr_user_id,
                    'label_name': curr_label,
                    'confidence_score': curr_confidence_score,
                    'result_timestamp': curr_result_timestamp
                })
        return ret_output

    except sqlite3.Error as e:
        print(f'SQLite error: {e}')
        return []

def set_preference(result_id):
    try:
        connection = sqlite3.connect(app.config['DATABASE'])
        cursor = connection.cursor()

        cursor.execute(f'UPDATE Results SET preferred = 1 WHERE result_id = {result_id}')
        connection.commit()
        connection.close()
        return True
    except sqlite3.Error as e:
        print(f'SQLite error: {e}')
        return False

def get_images_by_id(user_id, image_id_lst):
    ret_images = {}
    try:
        connection = sqlite3.connect(app.config['DATABASE'])
        cursor = connection.cursor()

        placeholder = ','.join(['?' for _ in range(len(image_id_lst))])
        cursor.execute(f'SELECT * FROM Images WHERE user_id = "{user_id}" AND image_id IN ({placeholder})', image_id_lst)
        rows = cursor.fetchall()
        connection.close()

        for row in rows:
            (curr_image_id, curr_user_id, curr_image_data, curr_file_path, curr_content_type, curr_upload_date) = row
            curr_obj = {
                'image_id': curr_image_id,
                'user_id': curr_user_id,
                'image_data': base64.b64encode(curr_image_data).decode('utf-8'),
                'upload_date': curr_upload_date
            }
            ret_images[curr_image_id] = curr_obj

        return ret_images
    except sqlite3.Error as e:
        print(f'SQLite error: {e}')
        return {}

def check_user(user_id):
    try:
        connection = sqlite3.connect(app.config['DATABASE'])
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM Images WHERE user_id = "{user_id}"')
        row = cursor.fetchone()
        connection.close()
        return True if row else False
    except sqlite3.Error as e:
        print(f'SQLite error: {e}')
        return False

@app.route('/results/<user_id>', methods=['GET'])
def get_results(user_id):
    print('Fetching results...')
    try:
        if not check_user(user_id):
            return jsonify({'error': 'No such user'}), 400
        

        ret_output = []
        results = fetch_results(user_id=user_id, selected=True)
        image_id_lst = [result['image_id'] for result in results]
        image_obj_dict = get_images_by_id(user_id, image_id_lst)

        


        for result in results:
            print('error is here')
            curr_output = {
                'image': image_obj_dict[result['image_id']],
                'result': result
            }
            ret_output.append(curr_output)


        ret_output.sort(key=lambda obj: obj['image']['upload_date'])
        return jsonify(ret_output), 200
    except Exception as e:
        print(f'Error in get_results: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    print('Analyzing...')
    try:
        if 'file' not in request.files or 'user_id' not in request.form:
            return jsonify({'error': 'File and user ID are required'}), 400

        file = request.files['file']
        user_id = request.form['user_id']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        result = perform_ai_processing(file)
        if not result:
            return jsonify({'error': 'failed to make inference'}), 400

        data = {
            'user_id': user_id,
            'image_data': file.read(),
            'file_path': file.filename,
            'content_type': file.content_type
        }

        image_id, result_id = store_in_database(data, result)
        if image_id is None or result_id is None:
            return jsonify({'error': 'failed to add data to database'}), 400

        results_lst = fetch_results(user_id, image_id)
        return jsonify(results_lst), 200
    except Exception as e:
        print(f'Error in analyze: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/select', methods=['POST'])
def select():
    print('Setting user preference...')
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing data'}), 400

        result_id = data['result_id']
        success = set_preference(result_id)

        if not success:
            return jsonify({'error': 'Invalid request'}), 400

        return jsonify({'message': 'Preference set successfully!'}), 200
    except Exception as e:
        print(f'Error in select: {e}')
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
