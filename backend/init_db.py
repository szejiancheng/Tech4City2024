import sqlite3

DATABASE = 'backend/database.db'

def init_db():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    ## Create table for uploaded images
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Images (
            image_id INTEGER UNIQUE NOT NULL,
            user_id TEXT NOT NULL, 
            image_data BLOB,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (image_id, user_id)
        );
    ''')
    print('Images table created!')

    # ## Create table for classification labels
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS Labels (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         label_name TEXT NOT NULL UNIQUE
    #     );
    # ''')
    # print('Labels table created!')

    ## Create table for classification results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            image_id INTEGER NOT NULL,
            label TEXT NOT NULL,
            confidence_score REAL,
            result_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (image_id) REFERENCES Images (image_id),
            FOREIGN KEY (user_id) REFERENCES Images (user_id)
        );
    ''')
    print('Results table created!')

    connection.commit()
    connection.close()


def check_db():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    ## Get list of tables
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = cursor.fetchall()
    print('Tables in the database:', tables)

    ## Check schema of Results table
    cursor.execute('PRAGMA table_info(Results);')
    results_schema = cursor.fetchall()
    print('Schema of the Results table:\n', results_schema)

    ## Check the schema of the Images table
    cursor.execute('PRAGMA table_info(Images);')
    images_schema = cursor.fetchall()
    print('Schema of the Images table:\n', images_schema)

    # ## Check the schema of the Labels table
    # cursor.execute('PRAGMA table_info(Labels);')
    # labels_schema = cursor.fetchall()
    # print('Schema of the Labels table:\n', labels_schema)

    connection.close()


init_db()
check_db()