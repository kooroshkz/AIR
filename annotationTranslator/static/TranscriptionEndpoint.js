// Initialize Speech Recognition
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = true; // Keep listening until stop
    recognition.interimResults = true; // Show intermediate results
    recognition.lang = "en-US"; 

    let lastFinalTranscript = ""; 

    // onresult gets called whenever the api detects action, like someone talking
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
        document.getElementById("output").innerText += `\n${finalTranscript}`; // Append final transcription
        lastFinalTranscript = finalTranscript; // Update last appended final transcription
      }

      document.getElementById("interimOutput").innerText = interimTranscript;
    };

    recognition.onerror = (event) => {
      console.error(`Error occurred: ${event.error}`);
    };

    // Start listening
    document.getElementById("startBtn").onclick = () => {

      recognition.start();
      console.log("Recognition started.");
    };

    // Stop listening
    document.getElementById("stopBtn").onclick = () => {
      recognition.stop();
      console.log("Recognition stopped.");
    };

document.getElementById('sendBtn').addEventListener('click', async () => {
    // Send the audio file via POST request
    const response = await fetch('/upload-transcription', {
        method: 'POST',
    headers: {
        'Content-Type': 'application/json' 
    },
        body: JSON.stringify({ text: document.getElementById("output").innerText})
    });


    const result = await response.json();

  //NOTE: result["model-output"] is a list containing JSON, not the JSON object itself
    LLMresponse = result["model-output"][0];
    
    console.log(LLMresponse);
    document.getElementById("LLMoutput").innerText += `\n${LLMresponse.generated_text}`;

    if (response.ok) {
        alert('Audio uploaded successfully!');
    } else {
        alert(`Error uploading audio: ${result.error}`);
    }
});

