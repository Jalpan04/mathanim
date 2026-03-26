const API_URL = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1') ? 'http://localhost:8000' : window.location.origin; // Dev vs Prod fallback
// For cleaner prod: const API_URL = ''; // Relative path if served from same root

const submitBtn = document.getElementById('submitBtn');
const problemInput = document.getElementById('problemInput');
const statusContainer = document.getElementById('statusContainer');
const statusText = document.getElementById('statusText');
const progressText = document.getElementById('progressText');
const progressBar = document.getElementById('progressBar');
const videoContainer = document.getElementById('videoContainer');
const resultVideo = document.getElementById('resultVideo');
const resultSource = document.getElementById('resultSource');
const downloadLink = document.getElementById('downloadLink');
const errorMessage = document.getElementById('errorMessage');

let pollInterval;
let currentTaskId = null; // Track ID for rating

submitBtn.addEventListener('click', async () => {
    const problem = problemInput.value.trim();
    if (!problem) return;

    // Reset UI
    resetUI();
    setLoading(true);
    updateStatus("Submitting problem...", 10);
    statusContainer.style.display = 'block';

    // Removed local let currentTaskId = null;

    try {
        const response = await fetch(`${API_URL}/solve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ problem })
        });

        if (!response.ok) throw new Error("Submission Failed");

        const data = await response.json();
        const taskId = data.task_id;
        currentTaskId = taskId; // Save for rating
        
        updateStatus("Queued for processing...", 20);
        
        // Start Polling
        pollStatus(taskId);

    } catch (error) {
        showError(error.message);
        setLoading(false);
    }
});

async function submitRating(rating) {
    if (!currentTaskId) return;
    
    // Visual Feedback: Highlight stars
    const stars = document.querySelectorAll('.stars span');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
            star.style.color = '#fbbf24';
        } else {
            star.classList.remove('active');
            star.style.color = '';
        }
    });

    // Text feedback
    const feedback = document.getElementById('ratingFeedback');
    feedback.innerText = "Saving learning...";
    feedback.style.display = 'block';

    try {
        await fetch(`${API_URL}/rate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: currentTaskId, rating: rating })
        });
        
        if (rating >= 5) {
            feedback.innerText = "Video Memorized! 🧠";
            // feedback.style.color = '#fbbf24'; // Removed per user request
        } else {
            feedback.innerText = "Rating Saved.";
            // feedback.style.color = '#fff';
        }
    } catch (e) {
        feedback.innerText = "Error saving rating.";
        feedback.style.color = '#ff4d4d';
    }
}

function pollStatus(taskId) {
    pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`${API_URL}/status/${taskId}`);
            const data = await res.json();

            if (data.status === 'completed') {
                clearInterval(pollInterval);
                updateStatus("Visualization Ready!", 100);
                showVideo(data.video_url);
                setLoading(false);
            } else if (data.status === 'failed') {
                clearInterval(pollInterval);
                showError(data.info || "Processing failed.");
                setLoading(false);
            } else {
                // Formatting status for display
                let displayStatus = "Processing...";
                let progress = 30;
                
                if (data.status === 'processing') {
                    displayStatus = "AI Agents are working... (Math -> Code -> Render)";
                    // Simulate checking infinite progress
                    const currentWidth = parseFloat(progressBar.style.width) || 30;
                    progress = Math.min(currentWidth + 5, 90);
                }
                
                updateStatus(displayStatus, progress);
            }
        } catch (e) {
            console.error(e);
        }
    }, 2000);
}

function updateStatus(text, percent) {
    statusText.innerText = text;
    progressText.innerText = `${Math.floor(percent)}%`;
    progressBar.style.width = `${percent}%`;
}

function showVideo(url) {
    // Ensure URL is correct. If relative, prepend API_URL
    const fullUrl = url.startsWith('http') ? url : `${API_URL}/${url}`;
    
    resultSource.src = fullUrl;
    resultVideo.load();
    videoContainer.style.display = 'block';
    
    downloadLink.href = fullUrl;
    
    // Show rating
    document.getElementById('ratingContainer').style.display = 'block';
}

function showError(msg) {
    errorMessage.innerText = msg;
    errorMessage.style.display = 'block';
}

function resetUI() {
    videoContainer.style.display = 'none';
    errorMessage.style.display = 'none';
    progressBar.style.width = '0%';
    resultSource.src = '';
    
    // Reset Rating
    document.getElementById('ratingContainer').style.display = 'none';
    document.getElementById('ratingFeedback').style.display = 'none';
    
    // Clear Star Visuals
    const stars = document.querySelectorAll('.stars span');
    stars.forEach(star => {
        star.classList.remove('active');
        star.style.color = '';
    });
}

function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    problemInput.disabled = isLoading;
    submitBtn.innerText = isLoading ? "Processing..." : "Generate Visualization";
    submitBtn.style.opacity = isLoading ? '0.7' : '1';
}
