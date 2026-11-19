/**
 * MemoryBridge AI — Routine Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  loadRoutineData();
});

async function loadRoutineData() {
  try {
    const baseline = await API.getRoutineBaseline();
    renderBaseline(baseline);

    const deviation = await API.getRoutineDeviation();
    renderDeviation(deviation);
  } catch (err) {
    console.error("Failed to load routine data:", err);
  }
}

function renderBaseline(steps) {
  const container = document.getElementById("baseline-steps-list");
  if (!container) return;

  if (!steps || steps.length === 0) {
    container.innerHTML = `<p style="color:#94a3b8; padding:1rem;">No baseline data defined.</p>`;
    return;
  }

  container.innerHTML = steps.map(step => `
    <div class="step-card">
      <div class="step-number">${step.step_order}</div>
      <div style="flex:1;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <strong style="color:#1e293b; font-size:0.95rem;">${step.activity}</strong>
          <span style="font-size:0.8rem; font-weight:700; color:var(--primary);">${step.typical_time}</span>
        </div>
        <div style="font-size:0.82rem; color:#64748b; margin-top:2px;">
          📍 ${step.location_name} • ${step.notes || ''}
        </div>
      </div>
    </div>
  `).join("");
}

function renderDeviation(dev) {
  const alertBox = document.getElementById("routine-alert-box");
  const alertTitle = document.getElementById("routine-alert-title");
  const alertMsg = document.getElementById("routine-alert-msg");
  const diffList = document.getElementById("routine-diff-points");
  const todayContainer = document.getElementById("today-steps-list");

  // Render Alert Box
  if (dev.is_deviated) {
    alertBox.style.display = "flex";
    alertTitle.innerText = "⚠️ " + dev.status_label;
    alertMsg.innerText = dev.summary_message;
    diffList.innerHTML = dev.deviation_points.map(pt => `<li>${pt}</li>`).join("");
  } else {
    alertBox.style.display = "none";
  }

  // Render Today's sequence
  if (!dev.current_sequence || dev.current_sequence.length === 0) {
    todayContainer.innerHTML = `<p style="color:#94a3b8; padding:1rem;">No activity logged yet today.</p>`;
    return;
  }

  todayContainer.innerHTML = dev.current_sequence.map((item, idx) => {
    const isDeviatedCard = dev.is_deviated && (item.includes("Hallway") || item.includes("re-entered") || item.includes("pacing"));
    return `
      <div class="step-card ${isDeviatedCard ? 'deviated' : ''}">
        <div class="step-number">${idx + 1}</div>
        <div style="flex: 1;">
          <div style="font-size: 0.92rem; font-weight: 600; color: #1e293b;">
            ${item}
          </div>
          ${isDeviatedCard ? '<span class="card-badge badge-uncertain" style="margin-top:4px; display:inline-block;">Oscillation Point</span>' : ''}
        </div>
      </div>
    `;
  }).join("");
}

async function triggerRoutineSim(scenario) {
  showToast(`Simulating ${scenario === 'routine_normal' ? 'normal baseline' : 'routine deviation'}...`);
  try {
    const res = await API.runDemoSimulation(scenario);
    showToast(res.message, "success");
    await loadRoutineData();
  } catch (err) {
    console.error(err);
    showToast("Failed to simulate routine: " + err.message, "danger");
  }
}
