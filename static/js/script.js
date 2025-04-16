// Connect to SocketIO server
const socket = io();

// Variables for audio recording
let mediaRecorder = null;

// Request microphone access and start recording
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                // Send each audio chunk to the server immediately
                const reader = new FileReader();
                reader.onload = () => {
                    const base64Audio = reader.result.split(',')[1];
                    socket.emit('audio_stream', { audio: base64Audio });
                };
                reader.readAsDataURL(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            console.log('Recording stopped');
            logMessage('Stopped recording');
        };

        mediaRecorder.start(100); // Generate chunks every 100ms
        console.log('Recording started');
        logMessage('Started recording');
    } catch (err) {
        console.error('Error accessing microphone:', err);
        logMessage('Error: Could not access microphone');
    }
}

// Stop recording
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
}

// Set language preference
function setLanguage() {
    const language = document.getElementById('language').value;
    socket.emit('set_language', { language: language });
    logMessage(`Selected language: ${language}`);
}

// Log messages to the chat div
function logMessage(message) {
    const chat = document.getElementById('chat');
    const p = document.createElement('p');
    p.textContent = message;
    chat.appendChild(p);
    chat.scrollTop = chat.scrollHeight;
}

// Handle connection
socket.on('connect', () => {
    console.log('Connected to server');
    logMessage('Connected to voice chat');
    setLanguage();
});

// Handle incoming audio stream
socket.on('audio_stream', (data) => {
    try {
        const audioBlob = new Blob([Uint8Array.from(atob(data.audio), c => c.charCodeAt(0))], { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
        logMessage('Received and playing original audio');
    } catch (err) {
        console.error('Error playing audio:', err);
        logMessage('Error: Failed to play audio');
    }
});

// Handle transcription
socket.on('transcription', (data) => {
    logMessage(`Transcription: ${data.text}`);
});

// Handle translation
socket.on('translation', (data) => {
    logMessage(`Translated (${data.language}): ${data.text}`);
});

// Handle TTS audio
socket.on('tts_audio', (data) => {
    try {
        const audioBlob = new Blob([Uint8Array.from(atob(data.audio), c => c.charCodeAt(0))], { type: 'audio/mp3' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
        logMessage(`Playing TTS audio in ${data.language}`);
    } catch (err) {
        console.error('Error playing TTS audio:', err);
        logMessage('Error: Failed to play TTS audio');
    }
});

// Handle errors from server
socket.on('error', (data) => {
    logMessage(`Error: ${data.message}`);
});