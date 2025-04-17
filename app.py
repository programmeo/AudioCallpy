from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import base64
from threading import Thread
from translator import transcribe_audio, translate_text, text_to_speech

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")  # Let SocketIO choose async mode

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

# Async processing for audio
def process_audio_async(audio_data, sender_sid, sender_language):
    try:
        transcription = transcribe_audio(audio_data)
        if not transcription:
            socketio.emit('error', {'message': 'Transcription failed'}, to=sender_sid)
            return
        print(f"Transcription: {transcription}")
        socketio.emit('transcription', {'text': transcription}, broadcast=True)
        for sid, target_language in user_languages.items():
            if sid != sender_sid:
                translated = transcription
                tts_audio = None
                if target_language != 'en' and sender_language != target_language:
                    translated = translate_text(transcription, target_language)
                    if not translated:
                        socketio.emit('error', {'message': f'Translation to {target_language} failed'}, to=sid)
                        continue
                    print(f"Translated to {target_language}: {translated}")
                    tts_audio = text_to_speech(translated, target_language)
                else:
                    tts_audio = text_to_speech(transcription, target_language)
                if not tts_audio:
                    socketio.emit('error', {'message': f'TTS for {target_language} failed'}, to=sid)
                    continue
                socketio.emit('translation', {'text': translated, 'language': target_language}, to=sid)
                print(f"Sending TTS audio to {sid} in {target_language}")
                socketio.emit('tts_audio', {'audio': tts_audio, 'language': target_language}, to=sid)
    except Exception as e:
        print(f"Async processing error: {e}")
        socketio.emit('error', {'message': 'Failed to process audio'}, to=sender_sid)

# WebSocket event: Receive audio chunk
@socketio.on('audio_stream')
def handle_audio_stream(data):
    try:
        audio_data = data['audio']
        sender_sid = request.sid
        sender_language = user_languages.get(sender_sid, 'en')
        Thread(target=process_audio_async, args=(audio_data, sender_sid, sender_language)).start()
    except Exception as e:
        print(f"Error processing audio: {e}")
        emit('error', {'message': 'Unexpected error processing audio'})

# WebSocket event: Client disconnects
@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    user_languages.pop(request.sid, None)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
