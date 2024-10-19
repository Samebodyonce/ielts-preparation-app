function setReminder() {
    if (!("Notification" in window)) {
        alert("This browser does not support desktop notification");
    } else if (Notification.permission === "granted") {
        scheduleNotification();
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(function (permission) {
            if (permission === "granted") {
                scheduleNotification();
            }
        });
    }
}

function scheduleNotification() {
    setTimeout(function() {
        new Notification("IELTS Preparation Reminder", {
            body: "It's time for your daily IELTS practice!",
        });
    }, 60000); // Notification will appear after 1 minute (for demo purposes)
}

function updateProgress(skill, score) {
    let progress = JSON.parse(localStorage.getItem('ieltsProgress')) || {};
    progress[skill] = score;
    localStorage.setItem('ieltsProgress', JSON.stringify(progress));
    displayProgress();
}

function displayProgress() {
    let progress = JSON.parse(localStorage.getItem('ieltsProgress')) || {};
    let progressHtml = '<h3>Your Progress</h3>';
    for (let skill in progress) {
        progressHtml += `<p>${skill}: ${progress[skill]}</p>`;
    }
    document.getElementById('progress-tracker').innerHTML = progressHtml;
}

// Call this function when the page loads
document.addEventListener('DOMContentLoaded', function() {
    displayProgress();
    setReminder();
});
