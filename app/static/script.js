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

// Detect if a string represents primarily a mathematical expression/formula
function isFormulaString(str) {
  if (!str) return false;
  const s = String(str).trim();
  // Check for LaTeX commands, math symbols, or delimiters
  if (/[\\[\]{}^_]|\$|\\(?:frac|int|iint|iiint|sqrt|sum|prod|cdot|pm|times|div|partial|infty|alpha|beta|gamma|theta|pi|sigma|sin|cos|tan|log|ln|dx|dy|dt)\b/.test(s)) {
    return true;
  }
  // Check for algebraic equations with numbers and operators (e.g. 2x + 5 = 15 or y = x^2 - 4)
  if (/[=<>≈]/.test(s) && (/[0-9]/.test(s) || /[+\-*/^]/.test(s))) {
    return true;
  }
  return false;
}

// Compile LaTeX expressions and math formulas into typeset KaTeX HTML
function compileLatex(text, forceDisplay = false) {
  if (!text) return "";
  const raw = String(text).trim();

  // If KaTeX CDN is not loaded, fallback gracefully to escaped text
  if (typeof katex === "undefined") {
    return escapeHtml(raw);
  }

  // 1. Check if string is enclosed in display math $$...$$ or \[...\]
  if (/^\$\$[\s\S]*\$\$$/.test(raw) || /^\\\[[\s\S]*\\\]$/.test(raw)) {
    const math = raw.replace(/^\$\$|^\\\[|\$\$$|\\\]$/g, "").trim();
    try {
      return katex.renderToString(math, { displayMode: true, throwOnError: false });
    } catch (_) {
      return escapeHtml(raw);
    }
  }

  // 2. Check if string is enclosed in inline math $...$ or \(...\)
  if (/^\$[\s\S]*\$$/.test(raw) || /^\\\(|\$$|\\\)$/.test(raw)) {
    const math = raw.replace(/^\$|^\\\(|\$$|\\\)$/g, "").trim();
    try {
      return katex.renderToString(math, { displayMode: forceDisplay, throwOnError: false });
    } catch (_) {
      return escapeHtml(raw);
    }
  }

  // 3. Standalone pure LaTeX equation (e.g. F(x) = \int (x^{2})\,dx = \frac{x^{3}}{3} + C)
  const hasLatexCommands = /\\(?:frac|int|iint|iiint|sqrt|sum|prod|cdot|pm|times|div|partial|infty|left|right|vec|mathbf|alpha|beta|gamma|theta|pi|sigma|sin|cos|tan|log|ln|dx|dy|dt)\b|\^|\_\{|\\[,;! ]/.test(raw);

  if (hasLatexCommands) {
    // Check if it's primarily an equation rather than an entire English paragraph
    const longWords = raw.replace(/\\(?:frac|sqrt|left|right|text|partial|times|cdot|int|sum)\{[^{}]*\}/g, "")
                         .match(/[A-Za-z]{5,}/g) || [];
    if (longWords.length <= 2) {
      try {
        return katex.renderToString(raw, { displayMode: forceDisplay, throwOnError: false });
      } catch (e) {
        console.warn("KaTeX render error on:", raw, e);
      }
    }
  }

  // 4. Mixed text with embedded $...$ or $$...$$ formulas
  const regex = /(\$\$[\s\S]+?\$\$|\$[^\$\n]+?\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\))/g;
  if (regex.test(raw)) {
    let segments = [];
    let lastIdx = 0;
    regex.lastIndex = 0;
    let match;

    while ((match = regex.exec(raw)) !== null) {
      if (match.index > lastIdx) {
        segments.push(escapeHtml(raw.slice(lastIdx, match.index)));
      }
      const token = match[0];
      let mathStr = token;
      let isBlock = false;
      if (token.startsWith("$$") || token.startsWith("\\[")) {
        mathStr = token.slice(2, -2).trim();
        isBlock = true;
      } else {
        mathStr = token.slice(1, -1).trim();
      }
      try {
        segments.push(katex.renderToString(mathStr, { displayMode: isBlock, throwOnError: false }));
      } catch (_) {
        segments.push(escapeHtml(token));
      }
      lastIdx = regex.lastIndex;
    }

    if (lastIdx < raw.length) {
      segments.push(escapeHtml(raw.slice(lastIdx)));
    }
    return segments.join("");
  }

  // 5. Handle inline expressions with LaTeX fragments like \frac{a}{b} or \sqrt{...}
  if (hasLatexCommands) {
    try {
      return katex.renderToString(raw, { displayMode: forceDisplay, throwOnError: false });
    } catch (_) {}
  }

  return escapeHtml(raw);
}

// Render the Step Breakdown panel with typeset LaTeX math
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

    let partA = s[0];
    let partB = s[1];
    let note = s[2];

    // Intelligently assign formula to .step-math and title/explanation to label/text
    const partAIsFormula = isFormulaString(partA);
    const partBIsFormula = isFormulaString(partB);

    let mathContent = partA;
    let textContent = partB;
    let titleContent = "";

    if (!partAIsFormula && partBIsFormula) {
      // e.g. partA is "Antiderivative" and partB is "F(x) = \int (x^2)\,dx = \frac{x^3}{3} + C"
      titleContent = partA;
      mathContent = partB;
      textContent = "";
    } else if (partAIsFormula && !partBIsFormula) {
      // e.g. partA is formula and partB is descriptive text
      mathContent = partA;
      textContent = partB;
    }

    let html = `<span class="step-idx">${idxStr}</span>` +
               `<div class="step-body">`;

    if (titleContent) {
      html += `<div class="step-label">${escapeHtml(titleContent)}</div>`;
    }

    html += `<div class="step-math">${compileLatex(mathContent, true)}</div>`;

    if (textContent) {
      html += `<div class="step-txt">${compileLatex(textContent, false)}</div>`;
    }

    if (note && note !== textContent && note !== titleContent) {
      html += `<div class="step-note">${compileLatex(note, false)}</div>`;
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
