# Cloud Control Tech4City 2024 Entry Coding Challenge Documentation

Thank you for considering Cloud Control for the Tech4City coding challenge! This documentation is meant to serve as a guide to explaining and running the **Nomsters** webapp, the AI powered food diary. The submission can be seen in this pull request [here](https://github.com/ej-hw/Tech4City2024/pull/14)

## Overview
When users upload pictures of food, the web app will return the name of the food item in the photo. The web app is a simple to use tool that conducts image classification using AI to determine food items in a photo.

**Note to users:** Since we are using assets that are stored in the frontend directory, the html file needs to be run via a http-server instead of the file directory (meaning the index.html cannot be clicked, as the file system via your browser cannot access the assets folder without violating a CORS policy)

1. To do so, if not already done, install http-server via your terminal using `npm install -g http-server`
2. In your terminal, navigate to the Tech4City2024/frontend and run `http-server -p 3000` (*Since our backend API occupies port 8000, as stated in the requirements, the frontend should use a different local port*)
   
## Features
- **Perform image recognition**:  Upload a photo through our intuitive UI, and choose the food label from a selection of our model's best guesses! 
- **Simple UI**: The web app is easy for users, old and new alike, to utilise. Uploading of photos is a intuitive, and results are clearly displayed. 
- **View past history**: A diary user interface is implemented to allow for easy navigation through past entries and predicted labels.
- **Login system**: A simple login system allows for users to retrieve and add to previously submitted food data despite different use sessions.  
## File Descriptions
### Frontend:
- `index.html`: The main HTML file for the app's user interface.
- `script.js`: JavaScript file for handling front-end logic and API interactions.
- `styles.css`: CSS file for styling the app.
### Backend:
- `model.py`: Python file implementing functionality for image recognition.
- `app.py`: Python file for the Flask server, handling API requests and interfacing with the database.
- `database.db`: SQLite database file for storing user and meal data.
- `API_documentation.yaml`: documentation for API endpoints of the server as it is in `app.py`
- `Dockerfile`: provides instructions for creating a Docker container
  
