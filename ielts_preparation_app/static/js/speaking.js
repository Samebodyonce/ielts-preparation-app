document.addEventListener('DOMContentLoaded', function() {
    const getTopicButton = document.getElementById('get-topic');
    const customTopicInput = document.getElementById('custom-topic');
    const topicDisplay = document.getElementById('topic-display');
    const startButton = document.getElementById('start-recording');
    const stopButton = document.getElementById('stop-recording');
    const submitButton = document.getElementById('submit-recording');
    const audioPlayback = document.getElementById('audio-playback');
    const results = document.getElementById('results');

    let mediaRecorder;
    let audioChunks = [];
    let currentTopic = '';

    getTopicButton.addEventListener('click', function() {
        fetch('/api/get_speaking_topic')
            .then(response => response.json())
            .then(data => {
                currentTopic = data.topic;
                topicDisplay.textContent = `Topic: ${currentTopic}`;
            });
    });

    customTopicInput.addEventListener('change', function() {
        currentTopic = this.value;
        topicDisplay.textContent = `Topic: ${currentTopic}`;
    });

    startButton.addEventListener('click', startRecording);
    stopButton.addEventListener('click', stopRecording);
    submitButton.addEventListener('click', submitRecording);

    function startRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();

                mediaRecorder.addEventListener("dataavailable", event => {
                    audioChunks.push(event.data);
                });

                startButton.disabled = true;
                stopButton.disabled = false;
            });
    }

    function stopRecording() {
        mediaRecorder.stop();
        startButton.disabled = false;
        stopButton.disabled = true;
        submitButton.disabled = false;

        mediaRecorder.addEventListener("stop", () => {
            const audioBlob = new Blob(audioChunks);
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayback.src = audioUrl;
            audioPlayback.style.display = 'block';
        });
    }

    function submitRecording() {
        if (currentTopic.trim() === '') {
            alert('Please select a topic or enter a custom one.');
            return;
        }

        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('topic', currentTopic);

        fetch('/api/analyze_speaking', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            let resultsHtml = '<h2>Analysis Results</h2>';
            resultsHtml += '<h3>Scores:</h3>';
            for (const [criterion, score] of Object.entries(data.scores)) {
                resultsHtml += `<p>${criterion}: ${score}</p>`;
            }
            resultsHtml += '<h3>Feedback:</h3>';
            data.feedback.forEach((item, index) => {
                resultsHtml += `<p>${index + 1}. ${item.aspect}: ${item.comment}</p>`;
            });
            resultsHtml += `<h3>Recommendations:</h3><p>${data.recommendations}</p>`;
            resultsHtml += `<h3>Topic Relevance:</h3><p>${data.topic_relevance}</p>`;
            results.innerHTML = resultsHtml;
        })
        .catch((error) => {
            console.error('Error:', error);
            results.innerHTML = '<p>An error occurred while analyzing the speech. Please try again.</p>';
        });
    }
});
