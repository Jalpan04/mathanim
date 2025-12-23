const API_URL = 'http://localhost:8000'; // Or relative '/' if served by same backend

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

submitBtn.addEventListener('click', async () => {
    const problem = problemInput.value.trim();
    if (!problem) return;

    // Reset UI
    resetUI();
    setLoading(true);
    updateStatus("Submitting problem...", 10);
    statusContainer.style.display = 'block';

    try {
        const response = await fetch(`${API_URL}/solve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ problem })
        });

        if (!response.ok) throw new Error("Submission Failed");

        const data = await response.json();
        const taskId = data.task_id;
        
        updateStatus("Queued for processing...", 20);
        
        // Start Polling
        pollStatus(taskId);

    } catch (error) {
        showError(error.message);
        setLoading(false);
    }
});

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
}

function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    problemInput.disabled = isLoading;
    submitBtn.innerText = isLoading ? "Processing..." : "Generate Visualization";
    submitBtn.style.opacity = isLoading ? '0.7' : '1';
}
