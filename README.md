Project Setup Instructions
Follow the steps below to set up and run the project, including API configuration, backend, frontend, and vector database setup.

1. Configuration
Add your Gemini API key in the config.py file:
GEMINI_KEY = "your_gemini_api_key_here"

2. Start Qdrant (Vector Database)
Use Docker to run Qdrant:
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

3. Backend Setup

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Navigate to the backend folder
cd back-end

# Setup the database
python setup_db.py

# Run the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000

4. Frontend Setup
cd front-end
streamlit run setup.py
Project Structure
.
├── config.py
├── requirements.txt
├── back-end/
│   ├── main.py
│   └── setup_db.py
└── front-end/
    └── setup.py


Notes
Ensure Docker is installed and running on your system for Qdrant.

Make sure ports 6333, 6334, and 8000 are free before running services.

The Streamlit frontend will launch in your browser automatically after startup.

