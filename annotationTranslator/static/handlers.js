let mediaRecorder;
let audioChunks = [];
let audioBlob;
let audioUrl;

const audioPlayer = document.getElementById("audioPlayer");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const sendBtn = document.getElementById("sendBtn");
const outputBox = document.getElementById("output");
const interimBox = document.getElementById("interimOutput");
const imageBtn = document.getElementById("imageInput");

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
	const imageFile = document.getElementById("imageInput").files[0];

	if (!imageFile) {
		alert("Please select an image.");
		return;
	}

	const formData = new FormData();
	const imageFormData = new FormData();

	currentDate = getTimestampFilename();
	formData.append("audio", audioBlob, currentDate);
	imageFormData.append("image", imageFile);

	const [audioResponse, textResponse, imageResponse] = await Promise.all([
		fetch("/upload-audio", {
			method: "POST",
			body: formData,
		}),
		fetch("/upload-transcription", {
			method: "POST",
			headers: {
				"content-type": "application/json",
			},
			body: JSON.stringify({
				text: outputBox.innerText,
			}),
		}),
		fetch("/upload-image", {
			method: "POST",
			body: imageFormData,
		}),
	]);

	const audioResult = await audioResponse.json();
	const llmResult = await textResponse.json();

	if (audioResponse.ok) {
		alert("Audio uploaded successfully!");
	} else {
		alert(`Error uploading audio: ${audioResponse.error}`);
	}

	if (textResponse.ok) {
		alert("Transcription uploaded successfully!");
	} else {
		alert(`Error uploading Transcription:  ${testResponse.error}`);
	}

	if (imageResponse.ok) {
		alert("Image uploaded successfully!");
	} else {
		alert(`Error uploading Image: ${testResponse.error}`);
	}

	//NOTE: result["model-output"] is a list containing JSON, not the JSON object itself
	llmResponse = llmResult["model-output"][0];

	console.log(llmResponse);
	document.getElementById("LLMoutput").innerText +=
		`\n${llmResponse.generated_text}`;

	document.getElementById("status").innerText =
		"Image uploaded!";
}

// Start recording when the "Start Recording" button is pressed
startBtn.addEventListener("click", startHandler);

// Stop recording when the stop gets pressed
stopBtn.addEventListener("click", stopHandler);

// Send the recorded audio to the server when the "Send Audio" button is pressed
sendBtn.addEventListener("click", sendHandler);

imageBtn.addEventListener("change", (event) => {
	const file = event.target.files[0];

	if (file) {
		const reader = new FileReader();
		reader.onload = (e) => {
			const imgPreview = document.getElementById("preview");
			imgPreview.src = e.target.result;
			imgPreview.style.display = "block";
		};
		reader.readAsDataURL(file);
	}
});
