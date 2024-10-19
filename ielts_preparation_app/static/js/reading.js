document.addEventListener('DOMContentLoaded', function() {
    const passage = document.getElementById('passage');
    const questions = document.getElementById('questions');
    const submitButton = document.getElementById('submit-answers');
    const results = document.getElementById('results');

    let currentTest = null;

    fetch('/api/get_reading_test')
        .then(response => response.json())
        .then(data => {
            currentTest = data;
            passage.innerHTML = `<p>${data.passage}</p>`;
            
            let questionsHtml = '';
            data.questions.forEach(question => {
                questionsHtml += `
                    <div class="question">
                        <p>${question.text}</p>
                        ${question.options.map(option => `
                            <label>
                                <input type="radio" name="q${question.id}" value="${option}">
                                ${option}
                            </label>
                        `).join('')}
                    </div>
                `;
            });
            questions.innerHTML = questionsHtml;
        });

    submitButton.addEventListener('click', function() {
        const userAnswers = {};
        currentTest.questions.forEach(question => {
            const selectedOption = document.querySelector(`input[name="q${question.id}"]:checked`);
            if (selectedOption) {
                userAnswers[question.id] = selectedOption.value;
            }
        });

        fetch('/api/check_reading_answers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({answers: userAnswers}),
        })
        .then(response => response.json())
        .then(data => {
            results.innerHTML = `
                <h2>Results</h2>
                <p>Score: ${data.score}/${data.total}</p>
                <p>Percentage: ${data.percentage.toFixed(2)}%</p>
            `;
        });
    });
});
