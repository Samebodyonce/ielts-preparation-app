document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const submitButton = document.getElementById('submit-button');
    const diagnosticButton = document.getElementById('diagnostic-button');
    const saveTargetsButton = document.getElementById('save-targets');
    let radarChart, lineChart;

    submitButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    diagnosticButton.addEventListener('click', function() {
        window.location.href = '/diagnostics';
    });

    saveTargetsButton.addEventListener('click', saveTargetSkills);

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessageToChat('You', message);
            userInput.value = '';

            fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({input: message}),
            })
            .then(response => response.json())
            .then(data => {
                addMessageToChat('Assistant', data.result);
                updateProgress();
            })
            .catch((error) => {
                console.error('Error:', error);
                addMessageToChat('Assistant', 'Sorry, an error occurred. Please try again.');
            });
        }
    }

    function addMessageToChat(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message';
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function updateProgress() {
        fetch('/api/get_progress')
            .then(response => response.json())
            .then(data => {
                updateRadarChart(data.current, data.targets);
                updateLineChart(data.history);
                if (data.recommendation) {
                    addMessageToChat('Assistant', data.recommendation);
                }
                // Обновляем значения в полях ввода целевых навыков
                document.getElementById('target-listening').value = data.targets.listening;
                document.getElementById('target-reading').value = data.targets.reading;
                document.getElementById('target-writing').value = data.targets.writing;
                document.getElementById('target-speaking').value = data.targets.speaking;
            })
            .catch(error => {
                console.error('Error updating progress:', error);
            });
    }

    function saveTargetSkills() {
        const targets = {
            listening: parseFloat(document.getElementById('target-listening').value),
            reading: parseFloat(document.getElementById('target-reading').value),
            writing: parseFloat(document.getElementById('target-writing').value),
            speaking: parseFloat(document.getElementById('target-speaking').value)
        };

        fetch('/api/save_target_skills', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(targets),
        })
        .then(response => response.json())
        .then(data => {
            alert('Target skills saved successfully!');
            updateProgress();
        })
        .catch(error => {
            console.error('Error saving target skills:', error);
            alert('Failed to save target skills. Please try again.');
        });
    }

    function updateRadarChart(current, targets) {
        const ctx = document.getElementById('radarChart').getContext('2d');
        if (radarChart) {
            radarChart.destroy();
        }
        radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: Object.keys(current),
                datasets: [
                    {
                        label: 'Current Skills',
                        data: Object.values(current),
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgb(255, 99, 132)',
                        pointBackgroundColor: 'rgb(255, 99, 132)',
                    },
                    {
                        label: 'Target Skills',
                        data: Object.values(targets),
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgb(54, 162, 235)',
                        pointBackgroundColor: 'rgb(54, 162, 235)',
                    }
                ]
            },
            options: {
                elements: {
                    line: {
                        borderWidth: 3
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            display: false
                        },
                        suggestedMin: 0,
                        suggestedMax: 9
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.formattedValue}`;
                            }
                        }
                    }
                }
            }
        });
    }

    function updateLineChart(history) {
        const ctx = document.getElementById('lineChart').getContext('2d');
        if (lineChart) {
            lineChart.destroy();
        }
        const datasets = Object.keys(history[0] || {}).filter(key => key !== 'date').map(skill => ({
            label: skill,
            data: history.map(entry => entry[skill]),
            borderColor: getColorForSkill(skill),
            fill: false
        }));

        lineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: history.map(entry => entry.date),
                datasets: datasets
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 9
                    }
                },
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    }
                }
            }
        });
    }

    function getColorForSkill(skill) {
        const colors = {
            listening: 'rgb(255, 99, 132)',
            reading: 'rgb(54, 162, 235)',
            writing: 'rgb(255, 206, 86)',
            speaking: 'rgb(75, 192, 192)'
        };
        return colors[skill] || 'rgb(201, 203, 207)';
    }

    updateProgress();
});
