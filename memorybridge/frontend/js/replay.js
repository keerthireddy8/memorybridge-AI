/**
 * MemoryBridge AI — Visual Memory Replay Controller & Canvas Animator
 */

// Canonical 4-step spatio-temporal demo trajectory
const REPLAY_STEPS = [
  {
    step: 1,
    time: "2:10 PM",
    title: "Keys Picked Up in Living Room",
    description: "Resident Eleanor Vance picked up house keys from the living-room coffee table.",
    location: "Living Room",
    zoneType: "activity",
    status: "VERIFIED",
    pos: { x: 120, y: 220 },
    hasKeys: true,
    privacyActive: false
  },
  {
    step: 2,
    time: "2:12 PM",
    title: "Traversed Living Room Toward Hallway",
    description: "Resident moved through the doorway into the central hallway while holding keys.",
    location: "Hallway",
    zoneType: "activity",
    status: "INFERRED",
    pos: { x: 280, y: 220 },
    hasKeys: true,
    privacyActive: false
  },
  {
    step: 3,
    time: "2:15 PM",
    title: "Keys Confirmed Entering Bedroom",
    description: "Resident and keys crossed the Bedroom threshold at 2:15 PM.",
    location: "Bedroom Threshold",
    zoneType: "boundary",
    status: "VERIFIED",
    pos: { x: 440, y: 220 },
    hasKeys: true,
    privacyActive: true
  },
  {
    step: 4,
    time: "2:15 PM",
    title: "Privacy Firewall Shield Engaged",
    description: "Visual camera tracking disengaged immediately. Observation halted at bedroom boundary.",
    location: "Bedroom",
    zoneType: "private",
    status: "ZONE_MASKED",
    pos: { x: 470, y: 220 },
    hasKeys: false, // Hidden behind privacy shield
    privacyActive: true
  }
];

let currentStepIdx = 0;
let isPlaying = false;
let playSpeed = 1.0;
let animationTimer = null;
let canvas, ctx;

document.addEventListener("DOMContentLoaded", () => {
  canvas = document.getElementById("replay-canvas");
  if (canvas) {
    ctx = canvas.getContext("2d");
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);
  }

  renderStepLedger();
  updateStepView(0);
  drawCanvas();
});

function resizeCanvas() {
  if (!canvas) return;
  canvas.width = canvas.parentElement.clientWidth;
  canvas.height = canvas.parentElement.clientHeight;
  drawCanvas();
}

// ================= Step Navigation & UI Updates =================
function updateStepView(idx) {
  currentStepIdx = Math.max(0, Math.min(idx, REPLAY_STEPS.length - 1));
  const step = REPLAY_STEPS[currentStepIdx];

  // Update scrubber
  const scrubber = document.getElementById("replay-scrubber");
  if (scrubber) scrubber.value = currentStepIdx;

  // Update detail card
  document.getElementById("step-counter-badge").innerText = `Step ${step.step} of ${REPLAY_STEPS.length}`;
  document.getElementById("step-time-title").innerText = `${step.time} — ${step.title}`;
  document.getElementById("step-description-text").innerText = step.description;

  const statusTag = document.getElementById("step-status-tag");
  statusTag.innerText = step.status;
  statusTag.className = `card-badge ${
    step.status === 'VERIFIED' ? 'badge-verified' :
    step.status === 'INFERRED' ? 'badge-inferred' : 'badge-uncertain'
  }`;

  const zoneTag = document.getElementById("step-zone-tag");
  zoneTag.innerText = step.zoneType === 'private' ? 'Private Zone (Shielded)' : 'Activity Zone (Observed)';
  zoneTag.className = `card-badge ${step.zoneType === 'private' ? 'badge-private' : 'badge-activity'}`;

  // Highlight in ledger
  document.querySelectorAll(".timeline-item").forEach((el, i) => {
    el.style.borderColor = (i === currentStepIdx) ? "var(--primary)" : "#e2e8f0";
    el.style.backgroundColor = (i === currentStepIdx) ? "#eef2ff" : "#f8fafc";
  });

  drawCanvas();
}

function nextStep() {
  if (currentStepIdx < REPLAY_STEPS.length - 1) {
    updateStepView(currentStepIdx + 1);
  } else {
    pauseReplay();
  }
}

function prevStep() {
  if (currentStepIdx > 0) {
    updateStepView(currentStepIdx - 1);
  }
}

function scrubStep(val) {
  pauseReplay();
  updateStepView(val);
}

function restartReplay() {
  pauseReplay();
  updateStepView(0);
}

function togglePlayPause() {
  if (isPlaying) {
    pauseReplay();
  } else {
    startReplay();
  }
}

function startReplay() {
  if (currentStepIdx >= REPLAY_STEPS.length - 1) {
    currentStepIdx = 0;
  }
  isPlaying = true;
  document.getElementById("btn-replay-play").innerText = "⏸";
  document.getElementById("replay-canvas-status").innerText = "Replay Playing...";

  const intervalMs = Math.round(2000 / playSpeed);
  clearInterval(animationTimer);
  animationTimer = setInterval(() => {
    if (currentStepIdx < REPLAY_STEPS.length - 1) {
      nextStep();
    } else {
      pauseReplay();
    }
  }, intervalMs);
}

function pauseReplay() {
  isPlaying = false;
  clearInterval(animationTimer);
  document.getElementById("btn-replay-play").innerText = "▶";
  document.getElementById("replay-canvas-status").innerText = "Replay Paused";
}

function changeSpeed(val) {
  playSpeed = parseFloat(val);
  if (isPlaying) {
    startReplay();
  }
}

// ================= Render Step Ledger =================
function renderStepLedger() {
  const container = document.getElementById("replay-chain-list");
  if (!container) return;

  container.innerHTML = REPLAY_STEPS.map((step, idx) => `
    <div class="timeline-item" onclick="scrubStep(${idx})" style="cursor: pointer;">
      <div class="timeline-time">${step.time}</div>
      <div class="timeline-content">
        <div class="timeline-desc">
          <strong>${step.title}</strong>
        </div>
        <div class="timeline-meta">
          <span class="card-badge ${step.status === 'VERIFIED' ? 'badge-verified' : 'badge-inferred'}">${step.status}</span>
          <span>${step.location}</span>
          ${step.privacyActive ? '<span class="card-badge badge-private">🔒 Privacy Active</span>' : ''}
        </div>
      </div>
    </div>
  `).join("");
}

// ================= Canvas Drawing =================
function drawCanvas() {
  if (!ctx || !canvas) return;

  const w = canvas.width;
  const h = canvas.height;

  // Clear
  ctx.fillStyle = "#0f172a";
  ctx.fillRect(0, 0, w, h);

  // Layout bounds
  const livingW = w * 0.45;
  const hallwayW = w * 0.22;
  const bedroomW = w * 0.33;

  // 1. Draw Living Room (Activity Zone)
  ctx.fillStyle = "#1e293b";
  ctx.fillRect(20, 40, livingW - 20, h - 80);
  ctx.strokeStyle = "#475569";
  ctx.lineWidth = 2;
  ctx.strokeRect(20, 40, livingW - 20, h - 80);

  ctx.fillStyle = "#94a3b8";
  ctx.font = "bold 14px sans-serif";
  ctx.fillText("🛋️ Living Room (Activity Zone)", 36, 70);

  // Coffee table in living room
  ctx.fillStyle = "#334155";
  ctx.fillRect(60, 160, 100, 120);
  ctx.strokeStyle = "#64748b";
  ctx.strokeRect(60, 160, 100, 120);
  ctx.fillStyle = "#cbd5e1";
  ctx.font = "12px sans-serif";
  ctx.fillText("Table", 90, 225);

  // 2. Draw Hallway
  ctx.fillStyle = "#1e293b";
  ctx.fillRect(livingW, 100, hallwayW, h - 200);
  ctx.strokeStyle = "#475569";
  ctx.strokeRect(livingW, 100, hallwayW, h - 200);
  ctx.fillStyle = "#94a3b8";
  ctx.fillText("🚶 Hallway", livingW + 15, 130);

  // 3. Draw Bedroom (Private Zone)
  const bedX = livingW + hallwayW;
  ctx.fillStyle = "#2e1065";
  ctx.fillRect(bedX, 40, bedroomW - 20, h - 80);
  ctx.strokeStyle = "#a855f7";
  ctx.lineWidth = 2;
  ctx.setLineDash([6, 4]);
  ctx.strokeRect(bedX, 40, bedroomW - 20, h - 80);
  ctx.setLineDash([]); // Reset dash

  ctx.fillStyle = "#e9d5ff";
  ctx.fillText("🛏️ Bedroom (Private Zone)", bedX + 16, 70);

  // Privacy boundary line
  ctx.strokeStyle = "#f43f5e";
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(bedX, 40);
  ctx.lineTo(bedX, h - 40);
  ctx.stroke();

  ctx.fillStyle = "#f43f5e";
  ctx.font = "bold 11px sans-serif";
  ctx.fillText("🔒 PRIVACY BOUNDARY", bedX - 60, h - 20);

  // If at step 3 or 4, draw Privacy Shield over Bedroom
  const curr = REPLAY_STEPS[currentStepIdx];
  if (curr.privacyActive) {
    ctx.fillStyle = "rgba(15, 23, 42, 0.88)";
    ctx.fillRect(bedX, 40, bedroomW - 20, h - 80);

    ctx.fillStyle = "#c084fc";
    ctx.font = "bold 16px sans-serif";
    ctx.fillText("🔒 PRIVACY SHIELD ACTIVE", bedX + 24, h / 2 - 10);
    ctx.font = "12px sans-serif";
    ctx.fillStyle = "#e2e8f0";
    ctx.fillText("Observation disengaged", bedX + 24, h / 2 + 15);
  }

  // Draw Trajectory Path Trail
  ctx.strokeStyle = "#818cf8";
  ctx.lineWidth = 3;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(110, h / 2);
  for (let i = 0; i <= currentStepIdx; i++) {
    const pt = getScaledPos(REPLAY_STEPS[i].pos, w, h);
    ctx.lineTo(pt.x, pt.y);
  }
  ctx.stroke();
  ctx.setLineDash([]);

  // Draw Resident Avatar at current position
  const currentPos = getScaledPos(curr.pos, w, h);

  // Glow
  const grad = ctx.createRadialGradient(currentPos.x, currentPos.y, 4, currentPos.x, currentPos.y, 24);
  grad.addColorStop(0, "rgba(99, 102, 241, 0.8)");
  grad.addColorStop(1, "rgba(99, 102, 241, 0)");
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(currentPos.x, currentPos.y, 24, 0, Math.PI * 2);
  ctx.fill();

  // Circle avatar
  ctx.fillStyle = "#4f46e5";
  ctx.beginPath();
  ctx.arc(currentPos.x, currentPos.y, 14, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "#ffffff";
  ctx.lineWidth = 2;
  ctx.stroke();

  // Label
  ctx.fillStyle = "#ffffff";
  ctx.font = "bold 12px sans-serif";
  ctx.fillText("👤 Eleanor", currentPos.x - 24, currentPos.y - 20);

  // Key marker if holding keys and not blinded
  if (curr.hasKeys) {
    ctx.fillStyle = "#f59e0b";
    ctx.beginPath();
    ctx.arc(currentPos.x + 14, currentPos.y + 10, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#000000";
    ctx.font = "10px sans-serif";
    ctx.fillText("🔑", currentPos.x + 8, currentPos.y + 14);
  }
}

function getScaledPos(pos, w, h) {
  // Base scale from 640x440
  return {
    x: (pos.x / 600) * w,
    y: (pos.y / 440) * h
  };
}
