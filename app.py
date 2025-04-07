'''This is the core file of the Flask application. See readme.md for more details.'''

import os
import logging
import requests
import json
import base64
import tempfile
from flask import Flask, render_template, request, jsonify, session
from gtts import gTTS
import uuid

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "spanish-learning-app-secret")

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define language levels and topics
LANGUAGE_LEVELS = {
    "beginner": "You are a Spanish language tutor helping a beginner. Use simple vocabulary, basic grammar, and very short sentences. Translate any complex terms.",
    "intermediate": "You are a Spanish language tutor helping an intermediate learner. Use moderate vocabulary, common expressions, and explain any difficult phrases.",
    "advanced": "You are a Spanish language tutor helping an advanced learner. Use rich vocabulary, idiomatic expressions, and complex grammar structures."
}

CONVERSATION_TOPICS = {
    "greetings": "basic greetings, introductions, and small talk",
    "travel": "traveling, directions, transportation, accommodation, and tourism",
    "food": "ordering food, discussing cuisine, recipes, and dining experiences",
    "shopping": "buying items, asking about prices, sizes, and preferences",
    "daily_life": "daily routines, schedules, and common activities",
    "work": "professional settings, job interviews, and workplace conversations",
    "health": "discussing health issues, visiting a doctor, and describing symptoms",
    "culture": "cultural events, traditions, and customs in Spanish-speaking countries"
}

# In-memory conversation history
conversations = {}

@app.route('/')
def index():
    """Render the main page of the application."""
    # Create a session ID if it doesn't exist
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # Initialize conversation history for this session if needed
    session_id = session['session_id']
    if session_id not in conversations:
        conversations[session_id] = []
    
    return render_template('index.html', 
                          language_levels=LANGUAGE_LEVELS.keys(),
                          topics=CONVERSATION_TOPICS.keys())

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process user message and return AI response with audio."""
    try:
        data = request.json
        user_message = data.get('message', '')
        level = data.get('level', 'beginner')
        topic = data.get('topic', 'greetings')
        
        # Get session ID
        session_id = session.get('session_id')
        if not session_id:
            session['session_id'] = str(uuid.uuid4())
            session_id = session['session_id']
            conversations[session_id] = []
        
        # Get conversation history
        conversation_history = conversations.get(session_id, [])
        
        # Construct the prompt for the LLM
        level_instruction = LANGUAGE_LEVELS.get(level, LANGUAGE_LEVELS['beginner'])
        topic_instruction = CONVERSATION_TOPICS.get(topic, CONVERSATION_TOPICS['greetings'])
        
        system_prompt = f"""
        {level_instruction}
        
        You're having a conversation in Spanish about {topic_instruction}. 
        Respond in Spanish, keep your responses natural and conversational.
        Use appropriate Spanish vocabulary and grammar for the {level} level.
        Keep responses concise (2-4 sentences).
        """
        
        # Build the full prompt with conversation history
        prompt = system_prompt + "\n\n"
        
        # Add conversation history (limiting to last 5 exchanges to avoid token limits)
        for msg in conversation_history[-5:]:
            if msg['role'] == 'user':
                prompt += f"User: {msg['content']}\n"
            else:
                prompt += f"Assistant: {msg['content']}\n"
        
        # Add the current user message
        prompt += f"User: {user_message}\nAssistant:"
        
        # Call Ollama API
        try:
            response = requests.post(
                OLLAMA_API_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            
            ai_message = response.json().get('response', 'Lo siento, no puedo responder en este momento.')
            logger.debug(f"AI response: {ai_message}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            ai_message = "Lo siento, tuve un problema técnico. Por favor, inténtalo de nuevo."
        
        # Generate speech from the AI message
        audio_base64 = text_to_speech(ai_message)
        
        # Store the conversation history
        conversation_history.append({'role': 'user', 'content': user_message})
        conversation_history.append({'role': 'assistant', 'content': ai_message})
        conversations[session_id] = conversation_history
        
        return jsonify({
            'message': ai_message,
            'audio': audio_base64
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your request',
            'message': 'Lo siento, ha ocurrido un error.'
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset the conversation history for the current session."""
    session_id = session.get('session_id')
    if session_id and session_id in conversations:
        conversations[session_id] = []
    
    return jsonify({'status': 'success'})

def text_to_speech(text):
    """Convert text to speech using gTTS and return as base64 encoded string."""
    try:
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as temp_audio:
            # Generate the speech
            tts = gTTS(text=text, lang='es', slow=False)
            tts.save(temp_audio.name)
            
            # Read the file and convert to base64
            temp_audio.seek(0)
            audio_content = temp_audio.read()
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            return audio_base64
    except Exception as e:
        logger.error(f"Error in text to speech conversion: {str(e)}")
        return ""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
