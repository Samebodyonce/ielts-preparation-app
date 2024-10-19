let currentSkill = '';
let diagnosticResults = {};
let mediaRecorder;
let audioChunks = [];

function startDiagnosticTest(skill) {
    currentSkill = skill;
    fetch(`/api/get_diagnostic_test/${skill}`)
        .then(response => response.json())
        .then(data => displayDiagnosticTest(data));
}

function displayDiagnosticTest(data) {
    let testHtml = `<h2>${currentSkill.charAt(0).toUpperCase() + currentSkill.slice(1)} Diagnostic Test</h2>`;
    
    if (currentSkill === 'reading') {
        testHtml += `<div class="passage">${data.passage}</div>`;
        data.questions.forEach((q, index) => {
            testHtml += createQuestionHtml(q, index);
        });
    } else if (currentSkill === 'listening') {
        data.forEach((q, index) => {
            testHtml += createQuestionHtml(q, index);
        });
    } else if (currentSkill === 'speaking') {
        testHtml += `
            <p>${data.question}</p>
            <button id="start-recording">Start Recording</button>
            <button id="stop-recording" disabled>Stop Recording</button>
            <audio id="audio-playback" controls style="display:none;"></audio>
        `;
    } else {
        data.forEach((q, index) => {
            testHtml += createQuestionHtml(q, index);
        });
    }
    
    testHtml += `<button onclick="submitDiagnosticTest()">Submit Test</button>`;
    document.getElementById('diagnostic-test').innerHTML = testHtml;

    if (currentSkill === 'speaking') {
        document.getElementById('start-recording').addEventListener('click', startRecording);
        document.getElementById('stop-recording').addEventListener('click', stopRecording);
    }
}

function createQuestionHtml(q, index) {
    let questionHtml = `<div class="question">`;
    if (q.audio_url) {
        questionHtml += `<audio controls src="/audio/${q.audio_url}"></audio>`;
    }
    if (q.question && currentSkill !== 'listening') {
        questionHtml += `<p>${index + 1}. ${q.question}</p>`;
    }
    if (q.task) {
        questionHtml += `<p>${index + 1}. ${q.task}</p>`;
    }
    if (q.options) {
        q.options.forEach(option => {
            questionHtml += `<label><input type="radio" name="q${index}" value="${option}"> ${option}</label><br>`;
        });
    } else if (currentSkill === 'writing' || currentSkill === 'speaking') {
        questionHtml += `<textarea name="q${index}" rows="4" cols="50"></textarea>`;
    }
    questionHtml += `</div>`;
    return questionHtml;
}

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
            });

            document.getElementById('start-recording').disabled = true;
            document.getElementById('stop-recording').disabled = false;
        });
}

function stopRecording() {
    mediaRecorder.stop();
    document.getElementById('start-recording').disabled = false;
    document.getElementById('stop-recording').disabled = true;

    mediaRecorder.addEventListener("stop", () => {
        const audioBlob = new Blob(audioChunks);
        const audioUrl = URL.createObjectURL(audioBlob);
        document.getElementById('audio-playback').src = audioUrl;
        document.getElementById('audio-playback').style.display = 'block';
    });
}

function submitDiagnosticTest() {
    let answers;
    if (currentSkill === 'speaking') {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        answers = [audioBlob];
    } else {
        answers = Array.from(document.querySelectorAll('.question')).map(q => {
            const input = q.querySelector('input[type="radio"]:checked') || q.querySelector('textarea');
            return input ? input.value : null;
        });
    }

    const formData = new FormData();
    if (currentSkill === 'speaking') {
        formData.append('audio', answers[0], 'recording.wav');
    } else {
        formData.append('answers', JSON.stringify(answers));
    }

    fetch(`/api/evaluate_diagnostic_test/${currentSkill}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        diagnosticResults[currentSkill] = data.score;
        displayDiagnosticResult(data.score);
    })
    .catch(error => {
        console.error('Error:', error);
        displayDiagnosticResult('Error');
    });
}

function displayDiagnosticResult(score) {
    document.getElementById('diagnostic-result').innerHTML = `
        <h3>${currentSkill.charAt(0).toUpperCase() + currentSkill.slice(1)} Diagnostic Result</h3>
        <p>Your estimated IELTS score: ${typeof score === 'number' ? score.toFixed(1) : 'N/A'}</p>
        <button onclick="nextDiagnosticTest()">Next Test</button>
    `;
}

function nextDiagnosticTest() {
    const skills = ['listening', 'reading', 'writing', 'speaking'];
    const nextSkillIndex = skills.indexOf(currentSkill) + 1;
    if (nextSkillIndex < skills.length) {
        startDiagnosticTest(skills[nextSkillIndex]);
    } else {
        saveDiagnosticResults();
    }
}

function saveDiagnosticResults() {
    fetch('/api/save_diagnostic_results', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(diagnosticResults)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Diagnostic results saved:', data);
        createLearningPlan();
    })
    .catch(error => {
        console.error('Error saving diagnostic results:', error);
    });
}

function createLearningPlan() {
    fetch('/api/create_learning_plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ results: diagnosticResults })
    })
    .then(response => response.json())
    .then(data => {
        displayLearningPlan(data.plan);
        // Добавляем перенаправление на страницу Adaptive Learning
        setTimeout(() => {
            window.location.href = '/adaptive_learning';
        }, 5000);  // Перенаправляем через 5 секунд, чтобы пользователь успел увидеть план обучения
    });
}

function displayLearningPlan(plan) {
    document.getElementById('learning-plan').innerHTML = `
        <h2>Your IELTS Diagnostic Results and Personalized Learning Plan</h2>
        <pre>${plan}</pre>
    `;
}
