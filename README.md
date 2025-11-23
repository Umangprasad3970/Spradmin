# Spradmin Project

This project is a Flask based admin dashboard using MongoDB backend.

## Features

- User management
- Restaurant management
- Notification management
- Subscription plans and history
- Admin profile with file upload
- MongoDB as database backend, integrated via pymongo and custom utilities.

## Running Locally

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the MongoDB setup (requires local or remote MongoDB instance running):
```
python mongodb_setup.py
```

3. Start the Flask app:
```
python app.py
```

4. Access at: http://localhost:5000

## Deployment

Designed for deployment on Render.com with remote MongoDB Atlas.

## Debug Data Route

Access `/debug-data` URL for raw data inspection from MongoDB.
