Flask Voice Chat with Translation and TTS
=========================================

Project Overview
----------------

This is a real-time voice chat application built with Flask and Flask-SocketIO. It allows users to:

*   Send voice messages via WebSockets.
*   Transcribe audio to text using Google Speech Recognition.
*   Translate text to users' preferred languages.
*   Convert translated text to audio (TTS) using Google Text-to-Speech.
*   Broadcast original audio, transcriptions, translations, and TTS audio to all connected clients (except the sender for TTS audio, based on their language).

The app is designed for production-grade use with scalability, error handling, and modularity.

File Structure
--------------
```
flask\_voice\_chat/
├── app.py                  # Main Flask-SocketIO application
├── translator.py           # Transcription, translation, and TTS logic
├── templates/
│   └── index.html          # Frontend HTML with UI
├── static/
│   └── script.js           # Client-side JavaScript for WebSocket and audio
├── requirements.txt        # Python dependencies
├── README.html             # This file
```

### File Descriptions

*   **app.py**: Core Flask app with SocketIO for WebSocket handling. Manages audio streams, language preferences, and broadcasts transcriptions, translations, and TTS audio.
*   **translator.py**: Contains functions for transcribing audio (speech-to-text), translating text, and generating TTS audio. Keeps logic modular and reusable.
*   **templates/index.html**: HTML frontend with a language selector, chat display, and buttons to start/stop recording.
*   **static/script.js**: JavaScript for capturing audio, sending/receiving WebSocket events, and playing original/TTS audio.
*   **requirements.txt**: Lists Python dependencies (Flask, Flask-SocketIO, gTTS, etc.).
*   **README.html**: Project documentation with setup and troubleshooting steps.

Installation Steps
------------------

Follow these steps to set up and run the application on your local machine.

1.  **Clone the Repository**
    
    If the project is in a repository, clone it. Otherwise, ensure all files are in a directory (e.g., `flask_voice_chat`).
    
        git clone <repository-url>
        cd flask_voice_chat
    
2.  **Create a Virtual Environment**
    
    Create and activate a Python virtual environment to isolate dependencies.
    
        python -m venv venv
        # On Windows:
        venv\Scripts\activate
        # On Linux/macOS:
        source venv/bin/activate
    
3.  **Install Dependencies**
    
    Install required Python packages from `requirements.txt`.
    
        pip install -r requirements.txt
    
4.  **Install FFmpeg**
    
    `pydub` requires FFmpeg for audio conversion. Install it based on your OS:
    
    *   Linux: `sudo apt install ffmpeg`
    *   macOS: `brew install ffmpeg`
    *   Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html), extract, and add to PATH.
5.  **Run the Application**
    
    Start the Flask server.
    
        python app.py
    
    Open [http://localhost:5000](http://localhost:5000) in multiple browser tabs.
    
6.  **Test the App**
    
    In each tab:
    
    *   Select a language (e.g., English, Spanish, French).
    *   Click "Start Recording", speak, and click "Stop Recording".
    *   Other tabs will play the original audio, show transcriptions/translations, and play TTS audio in their selected language (except the sender).
    

Error Troubleshooting
---------------------

Common issues and fixes based on typical setup problems.

*   **Flask-SocketIO Runtime Errors (e.g., AttributeError)**
    
    Ensure `request` is imported and `handle_connect` accepts an `auth` parameter. The provided `app.py` fixes this.
    
        # Example fix in app.py
        from flask import request
        @socketio.on('connect')
        def handle_connect(auth=None):
            ...
    
*   **ModuleNotFoundError: pkg\_resources**
    
    Install `setuptools`.
    
        pip install setuptools
    
*   **FFmpeg Not Found (pydub errors)**
    
    Verify FFmpeg installation and PATH configuration.
    
        # Test FFmpeg
        ffmpeg -version
    
    If missing, reinstall FFmpeg (see Installation Step 4).
    
*   **Transcription/Translation/TTS Failures**
    
    Google APIs (Speech Recognition, Translate, gTTS) require internet access and have free-tier limits.
    
    *   Check network connectivity.
    *   For production, use Google Cloud APIs with API keys.
    *   Log errors in `translator.py` for debugging.
*   **Audio Not Playing**
    
    Ensure browser supports WebM (original audio) and MP3 (TTS audio). Test in Chrome/Firefox.
    
    Check base64 decoding in `script.js`:
    
        console.log('Audio base64:', data.audio);
    
*   **Dependency Installation Fails**
    
    Ensure a C compiler is installed (e.g., Visual Studio Build Tools on Windows, `build-essential` on Linux).
    
        # Linux
        sudo apt install build-essential
    
*   **High Latency**
    
    Reduce audio chunk size in `script.js` (e.g., `mediaRecorder.start(50)`) or optimize network.
    

Production Notes
----------------

*   **Scalability**: Use Redis for WebSocket broadcasting (`pip install redis`, update `app.py` with `message_queue='redis://localhost:6379'`).
*   **Deployment**: Deploy with Gunicorn + Eventlet (`gunicorn --worker-class eventlet -w 1 app:socketio`).
*   **Security**: Restrict `cors_allowed_origins`, add authentication (e.g., Flask-Login).
*   **Monitoring**: Log errors to Sentry or similar.

Additional Resources
--------------------

*   [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
*   [gTTS Documentation](https://gtts.readthedocs.io/)
*   [deep\_translator Documentation](https://deep-translator.readthedocs.io/)
*   [SpeechRecognition Documentation](https://pypi.org/project/SpeechRecognition/)
