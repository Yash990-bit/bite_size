/**
 * BiteSize Web Dashboard
 * Connects to the BiteSize Python Agent Backend or runs local offline fallback.
 */

// State
let currentPlan = null;
let currentStepIndex = 0;
let streak = 0;
let dopamineScore = 0;
let timerInterval = null;
let timerSecondsRemaining = 120;
let isTimerRunning = false;
let audioContext = null;
let noiseNode = null;
let isBrownNoisePlaying = false;

// DOM Elements
const brainDumpInput = document.getElementById('brain-dump-input');
const deoverwhelmBtn = document.getElementById('deoverwhelm-btn');
const loadingIndicator = document.getElementById('loading-indicator');
const resultsSection = document.getElementById('results-section');
const loadSampleBtn = document.getElementById('load-sample-btn');
const clearInputBtn = document.getElementById('clear-input-btn');
const micBtn = document.getElementById('mic-btn');
const micLabel = document.getElementById('mic-label');

const audioToggleBtn = document.getElementById('audio-toggle-btn');
const soundIconOff = document.querySelector('.sound-icon-off');
const soundIconOn = document.querySelector('.sound-icon-on');
const soundStatusText = document.getElementById('sound-status-text');

const focusDomain = document.getElementById('focus-domain');
const focusTaskTitle = document.getElementById('focus-task-title');
const focusTaskDesc = document.getElementById('focus-task-desc');
const focusStepIndex = document.getElementById('focus-step-index');
const focusCompleteBtn = document.getElementById('focus-complete-btn');
const focusSkipBtn = document.getElementById('focus-skip-btn');
const buddyMessage = document.getElementById('buddy-message');

const timerMinutes = document.getElementById('timer-minutes');
const timerSeconds = document.getElementById('timer-seconds');
const timerStartPauseBtn = document.getElementById('timer-start-pause-btn');
const timerBtnText = document.getElementById('timer-btn-text');
const timerResetBtn = document.getElementById('timer-reset-btn');
const timerProgressCircle = document.getElementById('timer-progress-circle');

const progressFraction = document.getElementById('progress-fraction');
const progressFill = document.getElementById('progress-fill');
const streakCounter = document.getElementById('streak-counter');

const viewFocusModeBtn = document.getElementById('view-focus-mode-btn');
const viewAllModeBtn = document.getElementById('view-all-mode-btn');
const focusModeContainer = document.getElementById('focus-mode-container');
const allTasksContainer = document.getElementById('all-tasks-container');
const taskGroupsList = document.getElementById('task-groups-list');

const exportMarkdownBtn = document.getElementById('export-markdown-btn');
const printPlanBtn = document.getElementById('print-plan-btn');

const storyModal = document.getElementById('story-modal');
const openStoryBtn = document.getElementById('open-story-btn');
const closeStoryBtn = document.getElementById('close-story-btn');

// --- Brown Noise Generator (Web Audio API) ---
function toggleBrownNoise() {
  if (isBrownNoisePlaying) {
    stopBrownNoise();
  } else {
    startBrownNoise();
  }
}

function startBrownNoise() {
  try {
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioContext.state === 'suspended') {
      audioContext.resume();
    }

    const bufferSize = audioContext.sampleRate * 2;
    const noiseBuffer = audioContext.createBuffer(1, bufferSize, audioContext.sampleRate);
    const output = noiseBuffer.getChannelData(0);
    let lastOut = 0.0;

    for (let i = 0; i < bufferSize; i++) {
      const white = Math.random() * 2 - 1;
      output[i] = (lastOut + (0.02 * white)) / 1.02;
      lastOut = output[i];
      output[i] *= 3.5; // Gain adjustment
    }

    noiseNode = audioContext.createBufferSource();
    noiseNode.buffer = noiseBuffer;
    noiseNode.loop = true;

    const gainNode = audioContext.createGain();
    gainNode.gain.setValueAtTime(0.12, audioContext.currentTime);

    noiseNode.connect(gainNode);
    gainNode.connect(audioContext.destination);

    noiseNode.start();
    isBrownNoisePlaying = true;
    soundIconOff.classList.add('hidden');
    soundIconOn.classList.remove('hidden');
    soundStatusText.textContent = "Brown Noise: Playing";
    audioToggleBtn.style.borderColor = "var(--accent-emerald)";
  } catch (err) {
    console.error("Audio API error:", err);
  }
}

function stopBrownNoise() {
  if (noiseNode) {
    try { noiseNode.stop(); } catch(e) {}
    noiseNode.disconnect();
  }
  isBrownNoisePlaying = false;
  soundIconOff.classList.remove('hidden');
  soundIconOn.classList.add('hidden');
  soundStatusText.textContent = "Brown Noise: Off";
  audioToggleBtn.style.borderColor = "";
}

// --- Sample Backlog Loader ---
loadSampleBtn.addEventListener('click', () => {
  brainDumpInput.value = (
    "My room is a complete disaster clothes on floor desk covered in cups. " +
    "I have to finish my machine learning lab report due tonight but my code is broken, " +
    "and I haven't eaten lunch and need to reply to mom's message and wash dishes before roommate comes home."
  );
  brainDumpInput.focus();
});

clearInputBtn.addEventListener('click', () => {
  brainDumpInput.value = '';
  brainDumpInput.focus();
});

// --- Speech Recognition ---
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    micBtn.classList.add('active');
    micLabel.textContent = "Listening...";
  };

  recognition.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    brainDumpInput.value += (brainDumpInput.value ? " " : "") + transcript;
  };

  recognition.onend = () => {
    micBtn.classList.remove('active');
    micLabel.textContent = "Dictate";
  };

  micBtn.addEventListener('click', () => {
    try { recognition.start(); } catch(e) { recognition.stop(); }
  });
} else {
  micBtn.style.display = 'none';
}

// --- De-Overwhelm Action ---
deoverwhelmBtn.addEventListener('click', async () => {
  const dump = brainDumpInput.value.trim();
  if (!dump) {
    alert("Please pour out some thoughts first. Even a few words!");
    return;
  }

  const selectedLevel = document.querySelector('input[name="paralysis-level"]:checked')?.value || 'extreme';

  loadingIndicator.classList.remove('hidden');
  resultsSection.classList.add('hidden');

  try {
    // Attempt FastAPI endpoint
    const response = await fetch('/api/deoverwhelm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        brain_dump: dump,
        paralysis_level: selectedLevel,
        model_name: 'llama3.2:latest',
        user_name: 'Aarav'
      })
    });

    if (response.ok) {
      currentPlan = await response.json();
    } else {
      currentPlan = fallbackLocalDecompose(dump, selectedLevel);
    }
  } catch (err) {
    // Graceful offline fallback
    currentPlan = fallbackLocalDecompose(dump, selectedLevel);
  } finally {
    loadingIndicator.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    currentStepIndex = 0;
    renderCurrentStep();
    renderAllTasksList();
    updateProgressUI();
  }
});

// Client-side fallback if backend API is offline
function fallbackLocalDecompose(dump, level) {
  const lower = dump.toLowerCase();
  const steps = [];
  
  if (lower.includes('room') || lower.includes('clothes') || lower.includes('clean') || lower.includes('dishes')) {
    steps.push({
      id: "step-1",
      title: "Pick up 3 pieces of clothing from the floor",
      description: "Drop them into the hamper. Only 3 items. Don't fold anything.",
      domain: "Physical Space",
      estimated_seconds: 90,
      friction_score: 1,
      micro_reward: "🧺 +15 Clean Space Momentum",
      completed: false
    });
    steps.push({
      id: "step-2",
      title: "Relocate 2 empty cups from desk to kitchen sink",
      description: "Don't wash them right now. Just move them to the sink.",
      domain: "Physical Space",
      estimated_seconds: 60,
      friction_score: 1,
      micro_reward: "💧 +10 Desk Clarity",
      completed: false
    });
  }

  if (lower.includes('lab') || lower.includes('code') || lower.includes('report') || lower.includes('study')) {
    steps.push({
      id: "step-3",
      title: "Open the project file and read the first paragraph",
      description: "Do not write or fix anything yet. Just look at the screen for 60 seconds.",
      domain: "Academic & Work",
      estimated_seconds: 60,
      friction_score: 2,
      micro_reward: "💻 +20 Inertia Shattered",
      completed: false
    });
  }

  if (lower.includes('mom') || lower.includes('message') || lower.includes('email')) {
    steps.push({
      id: "step-4",
      title: "Send a 1-sentence placeholder reply",
      description: "Send: 'Hey! Got your message, busy right now but will call you by 7 PM!'",
      domain: "Administrative & Social",
      estimated_seconds: 45,
      friction_score: 2,
      micro_reward: "📱 +15 Social Relief",
      completed: false
    });
  }

  if (steps.length === 0) {
    steps.push({
      id: "step-1",
      title: "Stand up and take 3 deep belly breaths",
      description: "Snap the nervous system out of fight-or-flight freeze.",
      domain: "Self-Care",
      estimated_seconds: 45,
      friction_score: 1,
      micro_reward: "🫁 +10 Nervous Reset",
      completed: false
    });
  }

  return {
    session_id: "local_session",
    original_dump: dump,
    friction_analysis: {
      perceived_mountain: "Perceived mountain of mixed physical and mental chores.",
      core_blocker: "High task ambiguity and ADHD executive freeze.",
      paralysis_level: level
    },
    atomic_steps: steps,
    body_doubling_message: "Hey Aarav. Take a breath. You don't have to conquer your whole life today. Just give me 2 minutes on this single first step.",
    total_steps: steps.length
  };
}

// --- Focus Mode Rendering ---
function renderCurrentStep() {
  if (!currentPlan || !currentPlan.atomic_steps) return;
  const steps = currentPlan.atomic_steps;

  if (currentStepIndex >= steps.length) {
    // All done!
    focusDomain.textContent = "🎉 MISSION ACCOMPLISHED";
    focusTaskTitle.textContent = "You conquered all atomic micro-steps!";
    focusTaskDesc.textContent = "Inertia is completely broken. Celebrate this win and take a break.";
    focusStepIndex.textContent = `Completed ${steps.length} / ${steps.length}`;
    focusCompleteBtn.style.display = 'none';
    focusSkipBtn.style.display = 'none';
    triggerConfetti();
    return;
  }

  const step = steps[currentStepIndex];
  focusDomain.textContent = step.domain;
  focusTaskTitle.textContent = step.title;
  focusTaskDesc.textContent = step.description;
  focusStepIndex.textContent = `Step ${currentStepIndex + 1} of ${steps.length}`;
  focusCompleteBtn.style.display = 'inline-flex';
  focusSkipBtn.style.display = 'inline-flex';

  resetTimer(step.estimated_seconds || 120);
}

// --- 2-Minute Timer ---
function resetTimer(seconds = 120) {
  clearInterval(timerInterval);
  isTimerRunning = false;
  timerSecondsRemaining = seconds;
  updateTimerDisplay();
  timerBtnText.textContent = `Start ${Math.ceil(seconds / 60)}-Min Timer`;
  if (timerProgressCircle) {
    timerProgressCircle.style.strokeDashoffset = '0';
  }
}

function updateTimerDisplay() {
  const mins = Math.floor(timerSecondsRemaining / 60);
  const secs = timerSecondsRemaining % 60;
  timerMinutes.textContent = String(mins).padStart(2, '0');
  timerSeconds.textContent = String(secs).padStart(2, '0');
}

timerStartPauseBtn.addEventListener('click', () => {
  if (isTimerRunning) {
    clearInterval(timerInterval);
    isTimerRunning = false;
    timerBtnText.textContent = "Resume Timer";
  } else {
    isTimerRunning = true;
    timerBtnText.textContent = "Pause Timer";
    const totalSecs = currentPlan?.atomic_steps[currentStepIndex]?.estimated_seconds || 120;
    
    timerInterval = setInterval(() => {
      if (timerSecondsRemaining > 0) {
        timerSecondsRemaining--;
        updateTimerDisplay();
        const circumference = 326.7;
        const offset = circumference - (timerSecondsRemaining / totalSecs) * circumference;
        timerProgressCircle.style.strokeDashoffset = offset;
      } else {
        clearInterval(timerInterval);
        isTimerRunning = false;
        timerBtnText.textContent = "Time's Up!";
        triggerConfetti();
      }
    }, 1000);
  }
});

timerResetBtn.addEventListener('click', () => {
  const totalSecs = currentPlan?.atomic_steps[currentStepIndex]?.estimated_seconds || 120;
  resetTimer(totalSecs);
});

// --- Step Completion & Dopamine ---
focusCompleteBtn.addEventListener('click', async () => {
  if (!currentPlan) return;
  const step = currentPlan.atomic_steps[currentStepIndex];
  step.completed = true;

  streak++;
  dopamineScore += (15 * streak);
  currentStepIndex++;

  triggerConfetti();
  updateProgressUI();
  renderCurrentStep();
  renderAllTasksList();

  // Try reporting to backend
  try {
    await fetch('/api/complete-step', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ step_id: step.id })
    });
  } catch(e) {}
});

focusSkipBtn.addEventListener('click', () => {
  if (!currentPlan) return;
  currentStepIndex++;
  renderCurrentStep();
  renderAllTasksList();
});

function updateProgressUI() {
  if (!currentPlan) return;
  const total = currentPlan.atomic_steps.length;
  const completed = currentPlan.atomic_steps.filter(s => s.completed).length;
  progressFraction.textContent = `${completed} / ${total}`;
  const pct = total > 0 ? (completed / total) * 100 : 0;
  progressFill.style.width = `${pct}%`;
  streakCounter.textContent = `${streak} Streak`;
}

function renderAllTasksList() {
  if (!currentPlan) return;
  taskGroupsList.innerHTML = '';
  
  currentPlan.atomic_steps.forEach((step, idx) => {
    const card = document.createElement('div');
    card.className = `task-item-card ${step.completed ? 'completed' : ''}`;
    card.innerHTML = `
      <div>
        <span class="badge-tag" style="margin-bottom: 0.3rem;">${step.domain}</span>
        <h4 style="font-size: 0.95rem; margin-top: 0.2rem;">${idx + 1}. ${step.title}</h4>
        <p style="font-size: 0.8rem; color: var(--text-muted);">${step.description}</p>
      </div>
      <div style="text-align: right; white-space: nowrap;">
        <span style="font-size: 0.75rem; color: var(--accent-emerald-light);">${step.micro_reward}</span>
        <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.2rem;">${step.estimated_seconds}s</div>
      </div>
    `;
    taskGroupsList.appendChild(card);
  });
}

// Mode Toggles
viewFocusModeBtn.addEventListener('click', () => {
  focusModeContainer.classList.remove('hidden');
  allTasksContainer.classList.add('hidden');
  viewFocusModeBtn.classList.add('btn-primary');
  viewFocusModeBtn.classList.remove('btn-secondary');
  viewAllModeBtn.classList.add('btn-secondary');
  viewAllModeBtn.classList.remove('btn-primary');
});

viewAllModeBtn.addEventListener('click', () => {
  focusModeContainer.classList.add('hidden');
  allTasksContainer.classList.remove('hidden');
  viewAllModeBtn.classList.add('btn-primary');
  viewAllModeBtn.classList.remove('btn-secondary');
  viewFocusModeBtn.classList.add('btn-secondary');
  viewFocusModeBtn.classList.remove('btn-primary');
});

// Story Modal
openStoryBtn.addEventListener('click', () => storyModal.classList.remove('hidden'));
closeStoryBtn.addEventListener('click', () => storyModal.classList.add('hidden'));

// Export & Print
exportMarkdownBtn.addEventListener('click', () => {
  if (!currentPlan) return;
  let md = `# 🎯 BiteSize Action Plan\n\n`;
  currentPlan.atomic_steps.forEach(s => {
    md += `- [${s.completed ? 'x' : ' '}] **${s.title}** (${s.estimated_seconds}s) — *${s.description}*\n`;
  });
  navigator.clipboard.writeText(md).then(() => {
    alert("Copied clean Markdown checklist to clipboard!");
  });
});

printPlanBtn.addEventListener('click', () => window.print());

// Confetti Helper
function triggerConfetti() {
  if (typeof confetti === 'function') {
    confetti({
      particleCount: 40,
      spread: 60,
      origin: { y: 0.7 },
      colors: ['#10B981', '#34D399', '#6366F1', '#F59E0B']
    });
  }
}

// Audio Button Listener
audioToggleBtn.addEventListener('click', toggleBrownNoise);
