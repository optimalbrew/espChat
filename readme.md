# Spanish Conversation "replit" App using LLaMA

The initial code was generated from replit using this prompt. 
"make me an app to learn conversational spanish using a local LLM model such as llama3.2 from ollama for conversations with the agent. Use some text to speech software to convert the agent's response into audio so I can practice listening conversation"

The Flask app uses Google TTS. intial version didn't work, bcos the replit env does not actually run ollama. When informed, it modified the code to use openAI API instead for LLM backend. For that, it asked for an OpenAI API key. I want to run this app locally - using ollama. Which is what the current version does. However, it still  needs a web connection for the TTS. This can be replaced with something like PiperTTS - but had problems installing it on MacOS on Apple silicon (dependency piper phenomenize). 


## Features
- AI-driven conversational practice.
- Context-aware responses for natural dialogue.
- Customizable difficulty levels.


## Running the app

Clone the repository and install the dependencies - including Ollama with llama3.2!

Best to run in venv e.g if already in directory then

`python3 -m venv .` 

Then

`source bin/activate`

Python Packages: If any packages are missing, you can install them with:

`pip install flask flask-sqlalchemy gtts gunicorn requests`


Running the Spanish Learning App Locally

To run this app locally, you'll need to follow these steps:
Prerequisites

    Python 3.11 (already installed in this environment)
    Ollama with the Llama 3.2 model
    Required Python packages (already listed in the project)

Step-by-Step Guide
1. Install Ollama

2. Pull the Llama 3.2 Model e.g `ollama pull llama3.2` from terminal

3. Run Ollama

Start the Ollama server in a terminal:

`ollama serve` .. can set it to autostart, so this is not needed

This will start Ollama on localhost:11434, which is what our app expects.

4. Start the Flask Application

`gunicorn --bind 0.0.0.0:5001 --reuse-port --reload main:app`

5. Access the Application

Once the Flask app is running, you can access it through your web browser:

    In a local environment: http://localhost:5001

Troubleshooting

    Ollama Connection Error: If you see errors about failing to connect to Ollama, make sure the Ollama server is running on localhost:11434.

    Audio Not Playing: Some browsers may block autoplay of audio. You might need to click the play button manually the first time.

Using the App

    Select your language level (beginner, intermediate, advanced)
    Choose a conversation topic
    Type a message in English or Spanish
    The app will respond in Spanish and generate audio
    Listen to the pronunciation and continue the conversation



## Directory Structure


Main Application Files
1. `app.py`

This is the core file of the Flask application that:

    Sets up the Flask web server and configurations
    Defines the API endpoints for the chat functionality
    Handles conversation with the Ollama LLM (Llama 3.2 model)
    Manages text-to-speech conversion using gTTS (Google Text-to-Speech)
    Maintains conversation history for different user sessions

Key features:

    Language level selection (beginner, intermediate, advanced)
    Conversation topics (greetings, travel, food, etc.)
    REST API endpoints for chat and conversation reset

2. `main.py`

This is a simple entry point file that:

    Imports the Flask app from app.py
    Sets up logging for easier debugging
    Runs the Flask server on port 5001, accessible from any IP (0.0.0.0) .. initially the port was 5000, but I had something running on that already (apparently).  

Frontend Files
3. `templates/index.html`

The main HTML template for the web interface that:

    Provides a clean, Bootstrap-based UI with a dark theme
    Includes forms for user input and conversation settings
    Shows the conversation history and audio player
    Uses Feather icons for a modern look

4. `static/css/styles.css`

Contains custom CSS styles for:

    Conversation message bubbles
    Audio player styling
    Loading indicators
    Overall UI enhancements

5. `static/js/main.js`

Contains JavaScript that:

    Handles form submission for user messages
    Makes AJAX calls to the backend API
    Displays conversation messages in the UI
    Controls the audio player for text-to-speech playback
    Manages the conversation reset functionality

How the App Works

    The user selects their Spanish proficiency level and conversation topic
    They type a message in English or Spanish
    The message is sent to the backend where it calls the local Ollama LLM (Llama 3.2)
    The LLM generates a response in Spanish
    The Spanish response is converted to speech using gTTS
    Both the text response and audio are sent back to the frontend
    The user can listen to the pronunciation and continue the conversation

The application is designed to help users practice conversational Spanish by providing:

    Natural language responses based on user proficiency level
    Audio pronunciation of Spanish text
    Conversation topics relevant to real-world scenarios
    A clean, intuitive interface for practice sessions

Note: You need to have Ollama installed locally with the Llama 3.2 model. The application expects Ollama to be running on localhost:11434


## License
Not sure. I am not placing any restrictions of any kind. MIT would be nice. However, the initial code was generated by replit.com