console.log('script.js loaded successfully');

// Connect to SocketIO server
let socket;
try {
    socket = io();
    console.log('SocketIO initialized');
} catch (err) {
    console.error('SocketIO initialization failed:', err);
}

// Variables for audio recording
let mediaRecorder = null;
let audioChunks = [];
let stream = null;

// Request microphone access and start recording
async function startRecording() {
    console.log('startRecording called');
    try {
        // Step 1: Request microphone access
        console.log('Requesting microphone access...');
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log('Microphone access granted');

        // Step 2: Initialize MediaRecorder
        const mimeType = 'audio/webm;codecs=opus';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            throw new Error(`MIME type ${mimeType} not supported`);
        }
        mediaRecorder = new MediaRecorder(stream, { mimeType: mimeType });
        console.log('MediaRecorder initialized with MIME type:', mediaRecorder.mimeType);

        // Step 3: Set up data handling
        mediaRecorder.ondataavailable = (event) => {
            console.log('MediaRecorder data available, size:', event.data.size);
            if (event.data.size > 0) {
                audioChunks.push(event.data);
                const reader = new FileReader();
                reader.onload = () => {
                    const base64Audio = reader.result.split(',')[1];
                    console.log('Sending audio chunk to server');
                    socket.emit('audio_stream', { audio: base64Audio });
                };
                reader.readAsDataURL(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            console.log('Recording stopped');
            audioChunks = [];
        };

        // Step 4: Start recording
        mediaRecorder.start(500); // Send chunks every 500ms
        console.log('Recording started');
        logMessage('Started recording');
    } catch (err) {
        console.error('startRecording error:', err.name, err.message);
        if (err.name === 'NotAllowedError') {
            logMessage('Error: Microphone permission denied. Please allow microphone access in browser settings.');
        } else if (err.name === 'NotFoundError') {
            logMessage('Error: No microphone found. Please connect a microphone.');
        } else if (err.name === 'SecurityError') {
            logMessage('Error: Secure context required (use HTTPS or localhost).');
        } else {
            logMessage(`Error: Failed to start recording (${err.message})`);
        }
    }
}

// Stop recording
function stopRecording() {
    console.log('stopRecording called');
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        logMessage('Stopped recording');
    } else {
        console.log('No active recording to stop');
    }
}

// Set language preference
function setLanguage() {
    console.log('setLanguage called');
    const language = document.getElementById('language').value;
    socket.emit('set_language', { language: language });
    logMessage(`Selected language: ${language}`);
}

// Log messages to the chat div
function logMessage(message) {
    console.log('logMessage:', message);
    const chat = document.getElementById('chat');
    if (chat) {
        const p = document.createElement('p');
        p.textContent = message;
        chat.appendChild(p);
        chat.scrollTop = chat.scrollHeight;
    } else {
        console.error('Chat div not found');
    }
}

// Handle SocketIO connection
socket.on('connect', () => {
    console.log('SocketIO connected to server');
    logMessage('Connected to voice chat');
    setLanguage();
});

// Handle SocketIO connection error
socket.on('connect_error', (err) => {
    console.error('SocketIO connection error:', err);
    logMessage('Error: Failed to connect to server');
});

// Handle transcription
socket.on('transcription', (data) => {
    console.log('Received transcription:', data.text);
    logMessage(`Transcription: ${data.text}`);
});

// Handle translation
socket.on('translation', (data) => {
    console.log('Received translation:', data.text, 'Language:', data.language);
    logMessage(`Translated (${data.language}): ${data.text}`);
});

// Handle TTS audio
socket.on('tts_audio', (data) => {
    console.log('Received TTS audio for language:', data.language);
    try {
        if (!data.audio) throw new Error('No audio data received');
        const audioBytes = atob(data.audio);
        const audioBlob = new Blob([Uint8Array.from(audioBytes, c => c.charCodeAt(0))], { type: 'audio/mp3' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
        logMessage(`Playing TTS audio in ${data.language}`);
        audio.onended = () => URL.revokeObjectURL(audioUrl);
    } catch (err) {
        console.error('Error playing TTS audio:', err);
        logMessage('Error: Failed to play TTS audio');
    }
});

// Handle errors from server
socket.on('error', (data) => {
    console.log('Server error:', data.message);
    logMessage(`Error: ${data.message}`);
});