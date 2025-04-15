// Connect to the Socket.IO server
const socket = io();

// Get DOM elements
const startButton = document.getElementById('start-audio');
const stopButton = document.getElementById('stop-audio');
const userCount = document.getElementById('user-count');
const vadStatus = document.getElementById('vad-status');

// Initialize Web Audio API
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

// Handle start audio button click
startButton.addEventListener('click', () => {
    socket.emit('start_audio'); // Send start audio signal to server
    startButton.disabled = true; // Disable start button
    stopButton.disabled = false; // Enable stop button
});

// Handle stop audio button click
stopButton.addEventListener('click', () => {
    socket.emit('stop_audio'); // Send stop audio signal to server
    startButton.disabled = false; // Enable start button
    stopButton.disabled = true; // Disable stop button
    vadStatus.textContent = ''; // Clear speaking status
});

// Update user count when received from server
socket.on('user_count', (count) => {
    userCount.textContent = count; // Display number of connected users
});

// Update VAD status when received from server
socket.on('vad_status', (data) => {
    vadStatus.textContent = data.speaking ? 'Speaking...' : ''; // Show "Speaking..." if speaking
});

// Handle incoming audio stream
socket.on('audio_stream', (encodedData) => {
    // Decode base64 audio data
    const audioData = atob(encodedData);
    const arrayBuffer = new ArrayBuffer(audioData.length);
    const view = new Uint8Array(arrayBuffer);
    for (let i = 0; i < audioData.length; i++) {
        view[i] = audioData.charCodeAt(i);
    }
    
    // Convert to Float32Array for Web Audio API
    const floatArray = new Float32Array(arrayBuffer.byteLength / 2);
    const int16Array = new Int16Array(arrayBuffer);
    for (let i = 0; i < int16Array.length; i++) {
        floatArray[i] = int16Array[i] / 32768.0; // Convert 16-bit PCM to float
    }
    
    // Create audio buffer
    const audioBuffer = audioContext.createBuffer(1, floatArray.length, 16000);
    audioBuffer.copyToChannel(floatArray, 0);
    
    // Play audio
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.start();
});