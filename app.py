from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import pyaudio
import webrtcvad
import numpy as np
import threading
import queue
import base64

# Initialize Flask app and SocketIO for WebSocket communication
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'  # Secret key for session security
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS for WebSocket

# Audio configuration
CHUNK = 1024  # Number of audio frames per buffer
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Mono audio
RATE = 16000  # Sample rate in Hz (suitable for WebRTC VAD)
VAD = webrtcvad.Vad(3)  # Voice activity detection with aggressive mode (3)

# Store connected clients and audio queues
clients = set()  # Set to track connected client session IDs
audio_queues = {}  # Dictionary to store audio queues for each client
vad_status = {}  # Dictionary to track VAD status (speaking or not) for each client

# Route for the main page
@app.route('/ws')
def index():
    return render_template('index.html')  # Render the HTML template

# Handle new client connection
@socketio.on('connect')
def handle_connect():
    clients.add(request.sid)  # Add client session ID to clients set
    audio_queues[request.sid] = queue.Queue()  # Create a queue for this client's audio
    vad_status[request.sid] = False  # Initialize VAD status as not speaking
    emit('user_count', len(clients), broadcast=True)  # Broadcast current user count to all clients
    print(f"Client {request.sid} connected")

# Handle client disconnection
@socketio.on('disconnect')
def handle_disconnect():
    clients.remove(request.sid)  # Remove client from clients set
    del audio_queues[request.sid]  # Remove client's audio queue
    del vad_status[request.sid]  # Remove client's VAD status
    emit('user_count', len(clients), broadcast=True)  # Broadcast updated user count
    print(f"Client {request.sid} disconnected")

# Handle start audio request from client
@socketio.on('start_audio')
def start_audio():
    client_id = request.sid  # Get the client's session ID
    print(f"Starting audio for client {client_id}")

    # Function to capture and process audio
    def audio_pipeline():
        p = pyaudio.PyAudio()  # Initialize PyAudio
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)  # Open audio input stream
        
        try:
            while client_id in clients:  # Continue while client is connected
                data = stream.read(CHUNK, exception_on_overflow=False)  # Read audio chunk
                audio_queues[client_id].put(data)  # Put audio data in client's queue
                
                # Voice activity detection
                frame = np.frombuffer(data, dtype=np.int16)  # Convert audio to numpy array
                is_speech = VAD.is_speech(data, RATE)  # Check if the audio contains speech
                
                # Update VAD status if changed
                if vad_status[client_id] != is_speech:
                    vad_status[client_id] = is_speech
                    socketio.emit('vad_status', {'speaking': is_speech}, to=client_id)  # Send VAD status to client
                
                # Broadcast audio to all other clients
                encoded_data = base64.b64encode(data).decode('utf-8')  # Encode audio to base64 for transmission
                socketio.emit('audio_stream', encoded_data, skip_sid=client_id)  # Send audio to all except sender
        
        except Exception as e:
            print(f"Error in audio pipeline for {client_id}: {e}")
        finally:
            stream.stop_stream()  # Stop the audio stream
            stream.close()  # Close the stream
            p.terminate()  # Terminate PyAudio

    # Start audio pipeline in a separate thread
    threading.Thread(target=audio_pipeline, daemon=True).start()

# Handle stop audio request from client
@socketio.on('stop_audio')
def stop_audio():
    print(f"Stopping audio for client {request.sid}")

# Run the Flask app with SocketIO
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000, debug=True)