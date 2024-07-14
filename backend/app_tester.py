import sqlite3
from app import app
from init_db import init_db, check_db
import json

BASE_URL = 'http://127.0.0.1:8000'
DATABASE = 'backend/test_database.db'


## Test the /analyze endpoint
def analyze_query(test_client, image_data):
    print('Testing "/analyze" endpoint...')

    ## Specify content type
    headers = {'Content-Type': 'multipart/form-data'}  

    ## Request body
    data = {
        'file': image_data,
        'user_id': 'test_user'
    }
    
    ## Send image data in the request body
    response = test_client.post('/analyze', data=data, headers=headers)  

    return response


## Test the /select endpoint
def select_query(test_client, result_id):
    print('Testing "/select" endpoint...')

    ## Specify content type
    headers = {'Content-Type': 'application/json'}  

    ## Request body
    data = {
        'result_id': result_id
    }

    ## Send data to client
    response = test_client.post('/select', data=json.dumps(data), headers=headers)

    return response


## Test the /results/<user_id> endpoint
def results_query(test_client, user_id):
    print('Testing "/results/<user_id>" endpoint...')

    ## Redirect to user specific endpoint
    response = test_client.get(f'/results/{user_id}')

    return response

## Main method to execute all tests
def execute_tests(initialize_db=False, analyze=False, select=False, results=False):
    ## Initialize test database
    if initialize_db:
        init_db(DATABASE)
        check_db(DATABASE)
    app.config['DATABASE'] = DATABASE

    ## Create a test client
    app.testing = True
    client = app.test_client()

    ## Test /analyze path with image upload
    if analyze:
        with open('backend/static/ramen.jpg', 'rb') as image:
            analyze_response = analyze_query(client, image_data=image)
            print(analyze_response.text, analyze_response.status_code)

    ## Test /select with result_id
    result_id=33
    if select:
        select_response = select_query(client, result_id=result_id)
        print(select_response.text, select_response.status_code)

    ## Test /results/<user_id> with user_id = "test_user"
    if results:
        results_response = results_query(client, user_id='test_user')
        print(results_response.text, results_response.status_code)
    


def check_table(db, table_name):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    cursor.execute(f'''
        SELECT * FROM {table_name}
    ''')

    rows = cursor.fetchall()

    for row in rows:
        print(row)

    connection.close()


def clear_table(db, table_name):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    cursor.execute(f'''
        DELETE FROM {table_name}
    ''')
    connection.commit()

    connection.close()


if __name__ == '__main__':
    clear_table(DATABASE, 'Images')
    clear_table(DATABASE, 'Results')
    # execute_tests(analyze=True, select=True, results=True)
    # check_table(DATABASE, 'Results')