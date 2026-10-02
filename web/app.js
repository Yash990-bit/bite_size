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
        user_name: 'Mayank'
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

// Client-side dynamic deconstruction engine for arbitrary tasks
function fallbackLocalDecompose(dump, level) {
  // Strip emotional filler
  const cleaned = dump.replace(/(?i)\b(i have to|i need to|i must|i gotta|i should|im supposed to|panicking because|so overwhelmed with|feel completely frozen and|completely disaster|oh my god|omg)\b/gi, '');
  
  // Split on punctuation and natural language transitions
  const rawClauses = cleaned.split(/[\.\n;!\?]|(?:\b(?:and then|after that|and also|plus|before|also|need to|have to|and)\b)|,/i);
  const clauses = rawClauses.map(c => c.trim()).filter(c => c.length > 3 && !/^(it|that|then|so|but|is|are|a|an|the)$/i.test(c));

  const items = clauses.length > 0 ? clauses : [dump.trim()];
  const steps = [];

  items.forEach((clause, idx) => {
    const cl = clause.toLowerCase();
    let domain = "Life Management";
    let title = `Spend 60 seconds inspecting: ${clause}`;
    let desc = "Take one physical or digital action that takes under 120 seconds.";
    let reward = "⚡ +15 Action Initiated";
    let secs = 60;

    if (/water|drink|eat|lunch|dinner|breakfast|food|snack|hungry|pill|meds/i.test(cl)) {
      domain = "Self-Care";
      title = "Drink 1 glass of cold water and grab a quick bite";
      desc = "Blood sugar crashes trigger executive paralysis. Hydrate first.";
      reward = "🌱 +20 Energy Restored";
      secs = 60;
    } else if (/dish|dishes|sink/i.test(cl)) {
      domain = "Physical Space";
      title = "Squirt soap on 1 sponge and wash only 1 single fork or cup";
      desc = "Rinse 1 item and place on drying rack. Do not look at the rest.";
      reward = "✨ +15 Dish Inertia Shattered";
      secs = 60;
    } else if (/cloth|laundry|floor|room|mess/i.test(cl)) {
      domain = "Physical Space";
      title = "Pick up exactly 3 pieces of clothing from the floor";
      desc = "Toss them into the hamper. Only 3 items. Zero folding allowed.";
      reward = "🧺 +15 Floor Cleared";
      secs = 60;
    } else if (/code|bug|lab|report|study|exam|project|pr|git|write|slides/i.test(cl)) {
      domain = "Academic & Work";
      title = `Open your workspace or editor for: ${clause}`;
      desc = "Do not write or fix anything yet. Just open the window and look at it.";
      reward = "💻 +20 Inertia Shattered";
      secs = 60;
    } else if (/tax|taxes|bill|bank|pay|rent|landlord|renew|passport/i.test(cl)) {
      domain = "Administrative";
      title = `Create a desktop folder or bookmark link for: ${clause}`;
      desc = "Do not fill forms yet. Just create the destination folder or open the tab.";
      reward = "📁 +25 Bureaucracy Broken";
      secs = 45;
    } else if (/pack|suitcase|luggage|trip|bag/i.test(cl)) {
      domain = "Logistics";
      title = `Open your suitcase on the bed and lay out 2 pairs of socks`;
      desc = "Stop right there. You have successfully begun packing.";
      reward = "🧳 +20 Packing Begun";
      secs = 60;
    } else if (/dog|cat|vet|pet/i.test(cl)) {
      domain = "Pet Care";
      title = `Find the pet leash or carrier for: ${clause}`;
      desc = "Place it by the front door.";
      reward = "🐾 +15 Pet Care Step";
      secs = 45;
    } else if (/email|message|reply|text|call|mom|dad|friend/i.test(cl)) {
      domain = "Communication";
      title = `Send a 1-sentence placeholder reply for: ${clause}`;
      desc = "A 5-word acknowledgement is 100x better than ghosting.";
      reward = "📱 +15 Social Relief";
      secs = 45;
    }

    steps.push({
      id: `step-${idx + 1}`,
      title: title,
      description: desc,
      domain: domain,
      estimated_seconds: secs,
      friction_score: 1,
      micro_reward: reward,
      completed: false
    });
  });

  // Prioritize Self-Care first
  steps.sort((a, b) => (a.domain === "Self-Care" ? -1 : 1));

  return {
    session_id: "local_" + Math.random().toString(36).substring(7),
    original_dump: dump,
    friction_analysis: {
      perceived_mountain: `Overwhelming multi-task backlog with ${steps.length} fragmented items.`,
      core_blocker: "High task ambiguity and ADHD executive initiation freeze.",
      paralysis_level: level
    },
    atomic_steps: steps,
    body_doubling_message: "Hey Mayank. Take a breath. You don't have to conquer everything right now. Just give me 60 seconds on this single first step. I'm right here with you.",
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
