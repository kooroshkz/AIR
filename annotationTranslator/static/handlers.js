let mediaRecorder;
let audioChunks = [];
let audioBlob;
let audioUrl;

const audioPlayer = document.getElementById("audioPlayer");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const sendBtn = document.getElementById("sendBtn");
const outputBox = document.getElementById("output")
const interimBox = document.getElementById("interimOutput")

// Initialize Speech Recognition
const recognition = new (
	window.SpeechRecognition || window.webkitSpeechRecognition
)();
recognition.continuous = true; // Keep listening until stop
recognition.interimResults = true; // Show intermediate results
recognition.lang = "en-US";

let lastFinalTranscript = "";

recognition.onresult = (event) => {
	let finalTranscript = "";
	let interimTranscript = "";

	// Loop through the result array to get the transcriptions
	for (let i = event.resultIndex; i < event.results.length; i++) {
		const result = event.results[i];
		if (result.isFinal) {
			finalTranscript += result[0].transcript; // Add only final transcriptions
		} else {
			interimTranscript = result[0].transcript; // Store interim transcriptions (for preview)
		}
	}

	if (finalTranscript !== lastFinalTranscript) {
		outputBox.innerText += `\n${finalTranscript}`; // Append final transcription
		lastFinalTranscript = finalTranscript; // Update last appended final transcription
	}

	interimBox.innerText = interimTranscript;
};

recognition.onerror = (event) => {
	console.error(`Error occurred: ${event.error}`);
};



function getTimestampFilename(prefix = "upload", extension = "") {
	const now = new Date();
	const timestamp = now
		.toISOString()
		.replace(/[-:T]/g, "_") // Remove dashes, colons, and 'T'
		.split(".")[0]; // Remove milliseconds
	return `${prefix}_${timestamp}`;
}

async function startHandler() {
  
	recognition.start();
	console.log("Recognition started.");

	const stream = await navigator.mediaDevices.getUserMedia({
		audio: true,
	});
	mediaRecorder = new MediaRecorder(stream);

	// Collect audio data as it's recorded
	mediaRecorder.ondataavailable = (event) => {
		audioChunks.push(event.data);
	};

	// When recording stops, create a blob and update the audio player
	mediaRecorder.onstop = () => {
		audioBlob = new Blob(audioChunks, {
			type: "audio/wav",
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
}



function stopHandler() {

	recognition.stop();
	console.log("Recognition stopped.");

	mediaRecorder.stop();
	startBtn.disabled = false;
	stopBtn.disabled = true;
}

async function sendHandler() {
	const formData = new FormData();
	currentDate = getTimestampFilename();
	formData.append("audio", audioBlob, currentDate);

	// Send the audio file via POST request
	const response = await fetch("/upload-audio", {
		method: "POST",
		body: formData,
	});

	const result = await response.json();

	if (response.ok) {
		alert("Audio uploaded successfully!");
	} else {
		alert(`Error uploading audio: ${result.error}`);
	}

// Send the audio file via POST request
	const transcriptionResponse = await fetch("/upload-transcription", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({ text: document.getElementById("output").innerText }),
	});

	const TranscriptionResult = await transcriptionResponse.json();

	//NOTE: result["model-output"] is a list containing JSON, not the JSON object itself
	LLMresponse = TranscriptionResult["model-output"][0];

	console.log(LLMresponse);
	document.getElementById("LLMoutput").innerText +=
		`\n${LLMresponse.generated_text}`;

	if (transcriptionResponse.ok) {
		alert("Audio uploaded successfully!");
	} else {
		alert(`Error uploading audio: ${result.error}`);
	}
}

// Start recording when the "Start Recording" button is pressed
startBtn.addEventListener("click", startHandler);

// Stop recording when the stop gets pressed
stopBtn.addEventListener("click", stopHandler);

// Send the recorded audio to the server when the "Send Audio" button is pressed
sendBtn.addEventListener("click", sendHandler);
