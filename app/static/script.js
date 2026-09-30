const API_URL = window.location.origin;

let currentTaskId = null;
let pollInterval = null;
let lastGeneratedCode = "";

// DOM Elements
const problemInput = document.getElementById("problemInput");
const submitBtn = document.getElementById("submitBtn");
const statusContainer = document.getElementById("statusContainer");
const statusText = document.getElementById("statusText");
const progressText = document.getElementById("progressText");
const progressBar = document.getElementById("progressBar");
const errorMessage = document.getElementById("errorMessage");
const resultVideo = document.getElementById("resultVideo");
const resultSource = document.getElementById("resultSource");
const downloadLink = document.getElementById("downloadLink");
const ratingContainer = document.getElementById("ratingContainer");
const ratingFeedback = document.getElementById("ratingFeedback");
const examplesGrid = document.getElementById("examplesGrid");
const codeDisplay = document.getElementById("codeDisplay");
const modelBadge = document.getElementById("modelBadge");

// Pipeline Steps
const stepMath = document.getElementById("stepMath");
const stepArch = document.getElementById("stepArch");
const stepDev = document.getElementById("stepDev");
const stepRender = document.getElementById("stepRender");

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  loadSystemStatus();
  loadExamples();
});

// Load System Status
async function loadSystemStatus() {
  try {
    const res = await fetch(`${API_URL}/system-status`);
    if (res.ok) {
      const data = await res.json();
      if (modelBadge) {
        modelBadge.innerText = `${data.active_model}`;
      }
    }
  } catch (e) {
    console.warn("Could not fetch system status:", e);
  }
}

// Load Example Presets
async function loadExamples() {
  try {
    const res = await fetch(`${API_URL}/examples`);
    if (res.ok) {
      const examples = await res.json();
      if (examplesGrid) {
        examplesGrid.innerHTML = "";
        examples.forEach((item) => {
          const pill = document.createElement("button");
          pill.className = "example-pill";
          pill.innerText = `${item.category}: ${item.prompt}`;
          pill.onclick = () => {
            problemInput.value = item.prompt;
            problemInput.focus();
          };
          examplesGrid.appendChild(pill);
        });
      }
    }
  } catch (e) {
    console.warn("Could not load examples:", e);
  }
}

// Submit Problem
submitBtn.addEventListener("click", async () => {
  const problem = problemInput.value.trim();
  if (!problem) return;

  resetUI();
  setLoading(true);
  updateStatus("Initiating mathematical analysis...", 15, "math");
  statusContainer.style.display = "block";

  try {
    const res = await fetch(`${API_URL}/solve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ problem }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Submission failed");
    }

    const data = await res.json();
    currentTaskId = data.task_id;
    updateStatus("Agents processing problem...", 30, "arch");
    pollStatus(currentTaskId);
  } catch (err) {
    showError(err.message || "Network error. Please try again.");
    setLoading(false);
  }
});

// Poll Status
function pollStatus(taskId) {
  if (pollInterval) clearInterval(pollInterval);

  let ticks = 0;
  pollInterval = setInterval(async () => {
    ticks++;
    try {
      const res = await fetch(`${API_URL}/status/${taskId}`);
      if (!res.ok) throw new Error("Status query failed");

      const data = await res.json();

      if (data.status === "completed") {
        clearInterval(pollInterval);
        updateStatus("Visualization complete!", 100, "done");
        if (data.code) {
          lastGeneratedCode = data.code;
          codeDisplay.innerText = data.code;
        }
        showVideo(data.video_url);
        setLoading(false);
      } else if (data.status === "failed") {
        clearInterval(pollInterval);
        showError(data.info || "Animation generation failed.");
        if (data.code) {
          lastGeneratedCode = data.code;
          codeDisplay.innerText = data.code;
        }
        setLoading(false);
      } else {
        // Dynamic progress estimation
        let percent = 30;
        let step = "arch";
        let text = data.info || "Agents working...";

        if (ticks > 2 && ticks <= 5) {
          percent = 50;
          step = "dev";
          text = "Synthesizing Manim visual code...";
        } else if (ticks > 5 && ticks <= 12) {
          percent = 75;
          step = "render";
          text = "Compiling animation frames with Manim...";
        } else if (ticks > 12) {
          percent = Math.min(85 + (ticks - 12), 95);
          step = "render";
          text = "Finalizing video encode...";
        }

        updateStatus(text, percent, step);
      }
    } catch (e) {
      console.error("Polling error:", e);
    }
  }, 2500);
}

// Update Status and Steps
function updateStatus(text, percent, activeStep) {
  statusText.innerText = text;
  progressText.innerText = `${Math.floor(percent)}%`;
  progressBar.style.width = `${percent}%`;

  // Update step indicators
  const steps = [
    { el: stepMath, key: "math" },
    { el: stepArch, key: "arch" },
    { el: stepDev, key: "dev" },
    { el: stepRender, key: "render" },
  ];

  let passed = true;
  steps.forEach((s) => {
    s.el.classList.remove("active", "done");
    if (s.key === activeStep) {
      s.el.classList.add("active");
      passed = false;
    } else if (passed && percent > 20) {
      s.el.classList.add("done");
    }
  });

  if (percent >= 100) {
    steps.forEach((s) => s.el.classList.add("done"));
  }
}

// Show Video Output
function showVideo(videoUrl) {
  if (!videoUrl) return;
  const fullUrl = videoUrl.startsWith("http") ? videoUrl : `${API_URL}/${videoUrl}`;
  resultSource.src = fullUrl;
  resultVideo.load();
  resultVideo.play().catch(() => {});
  downloadLink.href = fullUrl;
  switchTab("video");
}

// Switch Tabs
function switchTab(tab) {
  const videoBtn = document.getElementById("tabVideoBtn");
  const codeBtn = document.getElementById("tabCodeBtn");
  const videoContent = document.getElementById("videoTabContent");
  const codeContent = document.getElementById("codeTabContent");

  if (tab === "video") {
    videoBtn.classList.add("active");
    codeBtn.classList.remove("active");
    videoContent.classList.add("active");
    codeContent.classList.remove("active");
  } else {
    codeBtn.classList.add("active");
    videoBtn.classList.remove("active");
    codeContent.classList.add("active");
    videoContent.classList.remove("active");
  }
}

// Copy Code
function copyGeneratedCode() {
  if (!lastGeneratedCode) return;
  navigator.clipboard.writeText(lastGeneratedCode).then(() => {
    const copyBtn = document.getElementById("copyCodeBtn");
    copyBtn.innerText = "Copied!";
    setTimeout(() => {
      copyBtn.innerText = "Copy Code";
    }, 2000);
  });
}

// Rating Feedback
async function submitRating(rating) {
  if (!currentTaskId) return;

  const stars = document.querySelectorAll(".star-rating span");
  stars.forEach((star, idx) => {
    if (idx < rating) {
      star.classList.add("active");
    } else {
      star.classList.remove("active");
    }
  });

  ratingFeedback.innerText = "Saving feedback...";
  try {
    const res = await fetch(`${API_URL}/rate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: currentTaskId, rating }),
    });
    if (res.ok) {
      ratingFeedback.innerText = rating >= 5 ? "Pattern memorized for future queries." : "Rating saved.";
    }
  } catch (e) {
    ratingFeedback.innerText = "Failed to submit rating.";
  }
}

function showError(msg) {
  errorMessage.innerText = msg;
  errorMessage.style.display = "block";
}

function resetUI() {
  if (pollInterval) clearInterval(pollInterval);
  errorMessage.style.display = "none";
  progressBar.style.width = "0%";
  resultSource.src = "";
  ratingFeedback.innerText = "";
  document.querySelectorAll(".star-rating span").forEach((s) => s.classList.remove("active"));
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  problemInput.disabled = isLoading;
  const btnText = submitBtn.querySelector(".btn-text");
  if (btnText) {
    btnText.innerText = isLoading ? "Synthesizing Animation..." : "Synthesize & Render Animation";
  }
}
