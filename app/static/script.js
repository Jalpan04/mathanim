const API_URL = (window.location.origin && window.location.origin.startsWith("http")) 
  ? window.location.origin 
  : "http://127.0.0.1:8000";

let currentTaskId = null;
let pollInterval = null;
let lastGeneratedCode = "";

// DOM Helper
const $ = (id) => document.getElementById(id);

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  loadSystemStatus();
  resetToIdle();

  // Button actions
  $('go').onclick = handleRender;
  $('replay').onclick = handleReplay;
  $('copyBtn').onclick = handleCopyCode;

  // Star rating events
  document.querySelectorAll('#starRating span').forEach((star) => {
    star.onclick = () => handleRating(parseInt(star.getAttribute('data-val'), 10));
  });
});

function resetToIdle() {
  $('stageIdle').style.display = 'flex';
  $('stageLoading').style.display = 'none';
  const video = $('resultVideo');
  video.pause();
  video.style.display = 'none';
  $('resultSource').src = "";
  $('pipelineTracker').style.display = 'none';
}

// Fetch active system model and hardware status
async function loadSystemStatus() {
  try {
    const res = await fetch(`${API_URL}/system-status`);
    if (res.ok) {
      const data = await res.json();
      if ($('modelBadge')) {
        $('modelBadge').innerText = data.active_model;
      }
    }
  } catch (e) {
    console.warn("System status unavailable:", e);
  }
}

// Submit Problem
async function handleRender() {
  const problem = $('q').value.trim();
  if (!problem) {
    $('q').focus();
    return;
  }

  hideError();
  setLoading(true);

  // Transition stage into active loading state
  $('stageIdle').style.display = 'none';
  const video = $('resultVideo');
  video.pause();
  video.style.display = 'none';
  $('resultSource').src = '';

  $('stageLoading').style.display = 'flex';
  $('loadingPrompt').innerText = problem;
  $('loadingStatus').innerText = 'Analyzing mathematical parameters & coordinates...';

  // Progress tracker
  $('pipelineTracker').style.display = 'block';
  updateProgress(15, 'Initiating mathematical analysis...');

  // Update drawers
  $('steps').innerHTML = '<div class="empty-state">Computing mathematical proof and step-by-step breakdown...</div>';
  $('codeDisplay').innerText = '# Synthesizing visual animation script...';

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
    updateProgress(30, "Synthesizing mathematical animation...");
    pollStatus(currentTaskId);
  } catch (err) {
    showError(err.message || "Failed to submit request.");
    setLoading(false);
    resetToIdle();
  }
}

// Poll Job Status
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
        updateProgress(100, "Animation ready");

        if (data.code) {
          lastGeneratedCode = data.code;
          $('codeDisplay').innerText = data.code;
        }

        if (data.math_solution) {
          const parsed = parseSolutionToSteps(data.math_solution);
          renderStepBreakdown(parsed);
        } else {
          $('steps').innerHTML = '<div class="empty-state">Completed successfully.</div>';
        }

        if (data.video_url) {
          displayVideo(data.video_url);
        }

        setTimeout(() => {
          $('pipelineTracker').style.display = 'none';
        }, 1200);

        setLoading(false);
      } else if (data.status === "failed") {
        clearInterval(pollInterval);
        showError(data.info || "Animation generation failed.");
        if (data.code) {
          lastGeneratedCode = data.code;
          $('codeDisplay').innerText = data.code;
        }
        setLoading(false);
        resetToIdle();
      } else {
        // Dynamic progress estimation
        let percent = 35;
        let text = data.info || "Agents working...";

        if (ticks > 2 && ticks <= 5) {
          percent = 55;
          text = "Synthesizing Manim visual code...";
        } else if (ticks > 5 && ticks <= 11) {
          percent = 78;
          text = "Compiling animation frames...";
        } else if (ticks > 11) {
          percent = Math.min(85 + (ticks - 11), 95);
          text = "Finalizing video encode...";
        }

        $('loadingStatus').innerText = text;
        updateProgress(percent, text);
      }
    } catch (e) {
      console.error("Polling error:", e);
    }
  }, 2000);
}

function updateProgress(percent, text) {
  $('trackerStatus').innerText = text;
  $('trackerPercent').innerText = `${Math.floor(percent)}%`;
  $('progressFill').style.width = `${percent}%`;
}

// Display Rendered MP4 Video inside the Stage
function displayVideo(videoUrl) {
  const fullUrl = videoUrl.startsWith("http") ? videoUrl : `${API_URL}/${videoUrl}`;
  const video = $('resultVideo');

  $('stageIdle').style.display = 'none';
  $('stageLoading').style.display = 'none';
  video.style.display = "block";

  $('resultSource').src = fullUrl;
  video.load();
  video.play().catch(() => {});

  // Update download link
  const dl = $('dl');
  dl.href = fullUrl;
  dl.style.display = "inline-flex";
}

function handleReplay() {
  const video = $('resultVideo');
  if (video.style.display !== "none" && $('resultSource').src) {
    video.currentTime = 0;
    video.play();
  }
}

function handleCopyCode() {
  const code = $('codeDisplay').innerText;
  if (!code) return;
  navigator.clipboard.writeText(code).then(() => {
    const btn = $('copyBtn');
    const original = btn.innerText;
    btn.innerText = "Copied!";
    setTimeout(() => { btn.innerText = original; }, 2000);
  });
}

async function handleRating(rating) {
  if (!currentTaskId) return;

  const stars = document.querySelectorAll('#starRating span');
  stars.forEach((s, idx) => {
    s.classList.toggle('active', idx < rating);
  });

  const feedback = $('ratingStatus');
  feedback.innerText = "Saving...";

  try {
    const res = await fetch(`${API_URL}/rate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: currentTaskId, rating }),
    });
    if (res.ok) {
      feedback.innerText = rating >= 5 ? "Pattern memorized." : "Saved.";
    }
  } catch (e) {
    feedback.innerText = "Error saving.";
  }
}

// Render the Step Breakdown drawer
function renderStepBreakdown(stepsData) {
  const stepsBlock = $('steps');
  stepsBlock.innerHTML = "";

  if (!stepsData || stepsData.length === 0) {
    stepsBlock.innerHTML = '<div class="empty-state">Step-by-step mathematical reasoning and construction steps will appear here upon rendering.</div>';
    return;
  }

  stepsData.forEach((s, i) => {
    const row = document.createElement('div');
    row.className = 'step-row';

    const idxStr = (i + 1) < 10 ? `0${i + 1}` : `${i + 1}`;
    let html = `<span class="step-idx">${idxStr}</span>` +
               `<div class="step-body">` +
                 `<div class="step-math">${escapeHtml(s[0])}</div>` +
                 `<div class="step-txt">${escapeHtml(s[1])}</div>`;

    if (s[2]) {
      html += `<div class="step-note">${escapeHtml(s[2])}</div>`;
    }

    html += `</div>`;
    row.innerHTML = html;
    stepsBlock.appendChild(row);
  });
}

// Parse mathematical solution text into structured steps
function parseSolutionToSteps(text) {
  if (!text) return null;
  const lines = text.split("\n").map(l => l.trim()).filter(l => l.length > 0);
  const steps = [];

  let headerContext = "";
  lines.forEach((line) => {
    const numMatch = line.match(/^(?:(?:Step\s*)?(\d+)[.:]\s*|(\d+)\.\s*)(.*)/i);
    if (numMatch) {
      const stepContent = numMatch[3];
      let mathPart = stepContent;
      let notePart = "";
      if (stepContent.includes(":")) {
        const parts = stepContent.split(":");
        mathPart = parts[0].trim();
        notePart = parts.slice(1).join(":").trim();
      }
      steps.push([
        mathPart,
        notePart || "Follow construction / calculation guideline.",
        headerContext || undefined
      ]);
    } else if (line.toLowerCase().includes("plan") || line.toLowerCase().includes("given") || line.toLowerCase().includes("property")) {
      headerContext = line;
    }
  });

  if (steps.length > 0) return steps;

  // Fallback: chunk lines into individual steps
  for (let i = 0; i < Math.min(lines.length, 5); i++) {
    steps.push([
      lines[i],
      "Sequential mathematical derivation step.",
      undefined
    ]);
  }
  return steps;
}

function setLoading(isLoading) {
  $('go').disabled = isLoading;
  $('q').disabled = isLoading;
  $('go').innerText = isLoading ? "Synthesizing Sequence..." : "Render Sequence";
}

function showError(msg) {
  const err = $('errorBanner');
  err.innerText = msg;
  err.style.display = "block";
}

function hideError() {
  const err = $('errorBanner');
  err.innerText = "";
  err.style.display = "none";
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
