const API_URL = (window.location.origin && window.location.origin.startsWith("http")) 
  ? window.location.origin 
  : "http://127.0.0.1:8000";

let currentTaskId = null;
let pollInterval = null;
let lastGeneratedCode = "";
let stageTimer = null;
let currentSteps = [];

// DOM Helper
const $ = (id) => document.getElementById(id);

// Initial default steps matching MathAnim Studio.html
const defaultSteps = [
  [
    '2x + 5 = 15', 
    'Start with the equation.',
    'Isolate the variable term (2x) by undoing addition first.'
  ],
  [
    '2x = 10', 
    'Subtract 5 from both sides.',
    'Whatever operation is applied to one side must be applied to the other to preserve equality: (2x + 5) - 5 = 15 - 5.'
  ],
  [
    'x = 5', 
    'Divide both sides by 2.',
    'Since x is multiplied by 2, perform the inverse operation (division by 2) to solve for x: 10 / 2 = 5.'
  ],
  [
    '2(5) + 5 = 15', 
    'Verify substitution result.',
    'Substitute x = 5 back into the original equation: 2(5) + 5 = 10 + 5 = 15. The solution holds true.'
  ]
];

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  renderStepBreakdown(defaultSteps);
  loadSystemStatus();
  loadExamples();
  playStageAnimation();

  // Button actions
  $('go').onclick = handleRender;
  $('replay').onclick = handleReplay;
  $('copyBtn').onclick = handleCopyCode;

  // Star rating events
  document.querySelectorAll('#starRating span').forEach((star) => {
    star.onclick = () => handleRating(parseInt(star.getAttribute('data-val'), 10));
  });
});

// Render the Step Breakdown drawer and Stage text elements
function renderStepBreakdown(stepsData) {
  currentSteps = stepsData;
  const stageSeq = $('stageSequence');
  const stepsBlock = $('steps');

  stageSeq.innerHTML = "";
  stepsBlock.innerHTML = "";

  stepsData.forEach((s, i) => {
    // Stage div
    const d = document.createElement('div');
    d.textContent = s[0];
    stageSeq.appendChild(d);

    // Step breakdown row
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

function showStageStep(n) {
  const d = $('stageSequence').children;
  for (let i = 0; i < currentSteps.length; i++) {
    if (d[i]) {
      d[i].className = i < n ? 'on' : i === n ? 'cur' : '';
    }
  }
}

function playStageAnimation() {
  clearInterval(stageTimer);
  let i = 0;
  showStageStep(-1);
  stageTimer = setInterval(() => {
    showStageStep(i);
    i++;
    if (i >= currentSteps.length) clearInterval(stageTimer);
  }, 2000);
  setTimeout(() => { showStageStep(0); i = 1; }, 50);
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

// Fetch preset examples and populate sidebar chips
async function loadExamples() {
  try {
    const res = await fetch(`${API_URL}/examples`);
    if (res.ok) {
      const examples = await res.json();
      const container = $('examplesContainer');
      container.innerHTML = "";
      examples.forEach((item) => {
        const btn = document.createElement("button");
        btn.className = "preset-chip";
        btn.title = item.prompt;
        btn.innerHTML = `<span class="chip-cat">${escapeHtml(item.category)}:</span> ${escapeHtml(item.prompt)}`;
        btn.onclick = () => {
          $('q').value = item.prompt;
          $('q').focus();
        };
        container.appendChild(btn);
      });
    }
  } catch (e) {
    console.warn("Could not load examples:", e);
  }
}

// Submit Problem
async function handleRender() {
  const problem = $('q').value.trim();
  if (!problem) return;

  hideError();
  setLoading(true);
  resetVideo();

  $('pipelineTracker').style.display = 'block';
  updateProgress(15, "Analyzing problem and geometry...");

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
    $('pipelineTracker').style.display = 'none';
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
          if (parsed && parsed.length > 0) {
            renderStepBreakdown(parsed);
          }
        }

        if (data.video_url) {
          displayVideo(data.video_url);
        }

        setTimeout(() => {
          $('pipelineTracker').style.display = 'none';
        }, 1500);

        setLoading(false);
      } else if (data.status === "failed") {
        clearInterval(pollInterval);
        showError(data.info || "Animation generation failed.");
        if (data.code) {
          lastGeneratedCode = data.code;
          $('codeDisplay').innerText = data.code;
        }
        setLoading(false);
        $('pipelineTracker').style.display = 'none';
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
  const stageSeq = $('stageSequence');

  clearInterval(stageTimer);
  stageSeq.style.display = "none";
  video.style.display = "block";

  $('resultSource').src = fullUrl;
  video.load();
  video.play().catch(() => {});

  // Update download link
  const dl = $('dl');
  dl.href = fullUrl;
  dl.style.display = "inline-flex";
}

function resetVideo() {
  const video = $('resultVideo');
  const stageSeq = $('stageSequence');
  video.pause();
  video.style.display = "none";
  $('resultSource').src = "";
  stageSeq.style.display = "flex";
  playStageAnimation();
}

function handleReplay() {
  const video = $('resultVideo');
  if (video.style.display !== "none" && $('resultSource').src) {
    video.currentTime = 0;
    video.play();
  } else {
    playStageAnimation();
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
      // Split math and explanation if colon or equal sign exists
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

  // Fallback: chunk lines into triplets
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
