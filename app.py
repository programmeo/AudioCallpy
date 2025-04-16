from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import base64
from translator import transcribe_audio, translate_text, text_to_speech

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Initialize SocketIO with eventlet
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Store user language preferences (key: session ID, value: language code)
user_languages = {}

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# WebSocket event: Client connects
@socketio.on('connect')
def handle_connect(auth=None):
    print(f'Client connected: {request.sid}')
    emit('message', {'data': 'Connected to voice chat!'})

# WebSocket event: Set user language preference
@socketio.on('set_language')
def handle_set_language(data):
    language = data.get('language', 'en')  # Default to English
    user_languages[request.sid] = language
    print(f"Set language for {request.sid} to {language}")
    emit('message', {'data': f'Language set to {language}'})

# WebSocket event: Receive audio chunk
@socketio.on('audio_stream')
def handle_audio_stream(data):
    try:
        audio_data = data['audio']
        sender_sid = request.sid
        sender_language = user_languages.get(sender_sid, 'en')  # Get sender's language

        # Transcribe audio
        transcription = transcribe_audio(audio_data)
        if transcription:
            print(f"Transcription: {transcription}")
            # Broadcast transcription to all clients
            emit('transcription', {'text': transcription}, broadcast=True)

            # Translate and generate TTS for all clients except sender
            for sid, target_language in user_languages.items():
                if sid != sender_sid:  # Skip sender
                    translated = transcription
                    tts_audio = None
                    if target_language != 'en' and sender_language != target_language:
                        # Translate only if sender's language differs from target
                        translated = translate_text(transcription, target_language)
                        if translated:
                            print(f"Translated to {target_language}: {translated}")
                            # Generate TTS audio for translated text
                            tts_audio = text_to_speech(translated, target_language)
                    else:
                        # Use transcription for English or same language
                        tts_audio = text_to_speech(transcription, target_language)

                    # Send translation and TTS audio to specific client
                    emit('translation', {'text': translated, 'language': target_language}, to=sid)
                    if tts_audio:
                        print(f"Sending TTS audio to {sid} in {target_language}")
                        emit('tts_audio', {'audio': tts_audio, 'language': target_language}, to=sid)
    except Exception as e:
        print(f"Error processing audio: {e}")
        emit('error', {'message': 'Failed to process audio'})

# WebSocket event: Client disconnects
@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    user_languages.pop(request.sid, None)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
