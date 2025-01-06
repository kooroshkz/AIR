let mediaRecorder;
let audioChunks = [];
let audioBlob;
let audioUrl;
let audioPlayer = document.getElementById('audioPlayer');
let startBtn = document.getElementById('startBtn');
let stopBtn = document.getElementById('stopBtn');
let sendBtn = document.getElementById('sendBtn');

function getTimestampFilename(prefix = 'upload', extension = '') {
    const now = new Date();
    const timestamp = now.toISOString()
        .replace(/[-:T]/g, '_') // Remove dashes, colons, and 'T'
        .split('.')[0]; // Remove milliseconds
    return `${prefix}_${timestamp}`;
}

// Start recording when the "Start Recording" button is pressed
startBtn.addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
        audio: true
    });
    mediaRecorder = new MediaRecorder(stream);

    // Collect audio data as it's recorded
    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    // When recording stops, create a blob and update the audio player
    mediaRecorder.onstop = () => {
        audioBlob = new Blob(audioChunks, {
            type: 'audio/wav'
        });
        //TODO: add multiple modes for recording, either clear the current audio blob on stopRecord, or on SendAudio
        audioChunks.length = 0; //clear the audio chunks to avoid new recordings just getting appended onto the existing one
        audioUrl = URL.createObjectURL(audioBlob);
        audioPlayer.src = audioUrl;
        sendBtn.disabled = false; 
    };

    mediaRecorder.start();
    startBtn.disabled = true; 
    stopBtn.disabled = false; 
});

// Stop recording when the stop gets pressed
stopBtn.addEventListener('click', () => {
    mediaRecorder.stop();
    startBtn.disabled = false; 
    stopBtn.disabled = true; 
});

// Send the recorded audio to the server when the "Send Audio" button is pressed
sendBtn.addEventListener('click', async () => {
    const formData = new FormData();
    currentDate = getTimestampFilename();
    formData.append('audio', audioBlob, currentDate); 

    // Send the audio file via POST request
    const response = await fetch('/upload-audio', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();

    if (response.ok) {
        alert('Audio uploaded successfully!');
    } else {
        alert('Error uploading audio: ' + result.error);
    }
});
