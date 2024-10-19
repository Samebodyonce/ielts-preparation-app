document.addEventListener('DOMContentLoaded', function() {
    const taskType = document.getElementById('task-type');
    const getTopicButton = document.getElementById('get-topic');
    const customTopicInput = document.getElementById('custom-topic');
    const topicDisplay = document.getElementById('topic-display');
    const essay = document.getElementById('essay');
    const submitButton = document.getElementById('submit-essay');
    const results = document.getElementById('results');

    let currentTopic = '';

    getTopicButton.addEventListener('click', function() {
        fetch('/api/get_writing_topic')
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

    submitButton.addEventListener('click', function() {
        const essayText = essay.value;
        const taskTypeValue = taskType.value;

        if (essayText.trim() === '') {
            alert('Please write an essay before submitting.');
            return;
        }

        if (currentTopic.trim() === '') {
            alert('Please select a topic or enter a custom one.');
            return;
        }

        fetch('/api/analyze_writing', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                essay: essayText,
                task_type: taskTypeValue,
                topic: currentTopic
            }),
        })
        .then(response => response.json())
        .then(data => {
            let resultsHtml = '<h2>Analysis Results</h2>';
            resultsHtml += '<h3>Scores:</h3>';
            for (const [criterion, score] of Object.entries(data.scores)) {
                resultsHtml += `<p>${criterion.replace('_', ' ')}: ${score}</p>`;
            }
            resultsHtml += '<h3>Improvements:</h3>';
            data.improvements.forEach((improvement, index) => {
                resultsHtml += `<p>${index + 1}. ${improvement.text}<br>Suggestion: ${improvement.suggestion}</p>`;
            });
            resultsHtml += `<h3>Recommendations:</h3><p>${data.recommendations}</p>`;
            resultsHtml += `<h3>Topic Relevance:</h3><p>${data.topic_relevance}</p>`;
            results.innerHTML = resultsHtml;
        })
        .catch((error) => {
            console.error('Error:', error);
            results.innerHTML = '<p>An error occurred while analyzing the essay. Please try again.</p>';
        });
    });
});
