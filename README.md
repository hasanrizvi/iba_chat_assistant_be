# IBA Chat Assistant (Backend)

## Steps to Build the Project

### 1. Create a Virtual Environment

First, set up a virtual environment to manage dependencies and isolate the project's environment.

```bash
# Example using virtualenv
virtualenv venv
# Activate the virtual environment (Windows)
venv\Scripts\activate
```

### 2. Install Package Dependencies

Install necessary packages listed in requirements.txt to ensure all dependencies are met.

```bash
pip install -r requirements.txt
```

### 3. Generate Training Data

Execute scrapper.py to gather and preprocess webpages, converting them into suitable training data for your model.

```bash
python scrapper.py
```

### 4. Update Environment Variable

Rename the .env.example to .env and add your HuggingFace Access Token


### 5. Train the Model and Start the Backend Server

Finally, run main.py to train your model using the prepared training data and start the backend server.

```bash
python main.py
```
