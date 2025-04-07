# Spanish Conversation "replit" App using LLaMA

The initial code was generated from replit using this prompt. 
"make me an app to learn conversational spanish using a local LLM model such as llama3.2 from ollama for conversations with the agent. Use some text to speech software to convert the agent's response into audio so I can practice listening conversation"

The Flask app uses Google TTS. intial version didn't work, bcos the replit env does not actually run ollama. When informed, it modified the code to use openAI API instead for LLM backend. For that, it asked for an OpenAI API key. I want to run this app locally - using ollama. 


## Features
- AI-driven conversational practice.
- Context-aware responses for natural dialogue.
- Customizable difficulty levels.

## Getting Started
1. Clone the repository.
2. Install dependencies.
3. Run the app and start practicing!

## Directory Structure

I asked replit to walk me through the directory explaining the role of main files. Below is the reponse

### Replit's explanation of the code

Spanish Learning Conversation App Directory Overview

Let me walk you through the main files in this application and explain their functions:
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
    Runs the Flask server on port 5000, accessible from any IP (0.0.0.0)

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

Note: To make this app fully functional, you need to have Ollama installed locally with the Llama 3.2 model. The application expects Ollama to be running on localhost:11434.

## Running the app
Asked replit to provide a walk through of how to run the app locally. This is the response.

Running the Spanish Learning App Locally

To run this app locally, you'll need to follow these steps:
Prerequisites

    Python 3.11 (already installed in this environment)
    Ollama with the Llama 3.2 model
    Required Python packages (already listed in the project)

Step-by-Step Guide
1. Install Ollama

First, you need to install Ollama, which is a tool to run LLMs locally.

# On macOS or Linux
curl -fsSL https://ollama.com/install.sh | sh

# On Windows
# Download from https://ollama.com/download

2. Pull the Llama 3.2 Model

After installing Ollama, you need to pull the Llama 3.2 model:

ollama pull llama3.2

This might take some time as it's downloading a large language model.
3. Run Ollama

Start the Ollama server in a terminal:

ollama serve

This will start Ollama on localhost:11434, which is what our app expects.
4. Start the Flask Application

Now, you can start the Flask application. Since we're in a Replit environment, we can use the workflow:

# Use Replit's workflow
restart_workflow "Start application"

# Or run directly with
gunicorn --bind 0.0.0.0:5001 --reuse-port --reload main:app

5. Access the Application

Once the Flask app is running, you can access it through your web browser:

    In a local environment: http://localhost:5001
    In Replit: Use the webview or the provided URL

Troubleshooting

    Ollama Connection Error: If you see errors about failing to connect to Ollama, make sure the Ollama server is running on localhost:11434.
    Missing Python Packages: If any packages are missing, you can install them with:

    pip install flask flask-sqlalchemy gtts gunicorn requests

    Audio Not Playing: Some browsers may block autoplay of audio. You might need to click the play button manually the first time.

Using the App

    Select your language level (beginner, intermediate, advanced)
    Choose a conversation topic
    Type a message in English or Spanish
    The app will respond in Spanish and generate audio
    Listen to the pronunciation and continue the conversation

Let me know if you'd like to test the application or if you run into any issues!


## License
Not sure. The initial code was generated by replit