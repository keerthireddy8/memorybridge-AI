/**
 * MemoryBridge AI — Caregiver Digest Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  loadCaregiverData();
});

async function loadCaregiverData() {
  try {
    // 1. Medicine Anchor
    const medAnchor = await API.getMedicineAnchor();
    const medEl = document.getElementById("care-med-status");
    if (medAnchor && medAnchor.has_anchor) {
      medEl.innerText = `Recorded (${medAnchor.last_interaction_time})`;
      medEl.style.color = "#059669";
    } else {
      medEl.innerText = "No Record Yet";
      medEl.style.color = "#d97706";
    }

    // 2. Routine Deviation Check
    const routine = await API.getRoutineDeviation();
    const routineStatusEl = document.getElementById("care-routine-status");
    const routineSubEl = document.getElementById("care-routine-sub");
    const devBanner = document.getElementById("care-deviation-banner");
    const devText = document.getElementById("care-deviation-text");

    if (routine.is_deviated) {
      routineStatusEl.innerText = "Deviation Detected";
      routineStatusEl.style.color = "#d97706";
      routineSubEl.innerText = routine.deviation_points[0] || "Pacing detected";
      devBanner.style.display = "flex";
      devText.innerText = routine.summary_message + " " + (routine.deviation_points[0] || "");
    } else {
      routineStatusEl.innerText = "Routine Aligned";
      routineStatusEl.style.color = "#059669";
      routineSubEl.innerText = "Consistent with morning baseline";
      devBanner.style.display = "none";
    }

    // 3. Filtered Important Events
    const events = await API.getEvents(30);
    renderCaregiverDigest(events);
  } catch (err) {
    console.error("Failed to load caregiver data:", err);
  }
}

function renderCaregiverDigest(events) {
  const container = document.getElementById("care-timeline-list");
  if (!container) return;

  // Filter for key anchor events: medicine, key moves, room exits/entries, boundary transits
  const keyEvents = events.filter(e => 
    e.object_id === "obj_medicine" ||
    e.object_id === "obj_keys" ||
    e.privacy_status === "BOUNDARY_CROSSED" ||
    e.verification_status === "VERIFIED"
  );

  if (keyEvents.length === 0) {
    container.innerHTML = `<p style="text-align:center; color:#94a3b8; padding:2rem;">No vital anchor events logged yet today.</p>`;
    return;
  }

  container.innerHTML = keyEvents.map(ev => {
    let icon = "📍";
    if (ev.object_id === "obj_medicine") icon = "💊";
    else if (ev.object_id === "obj_keys") icon = "🔑";
    else if (ev.privacy_status === "BOUNDARY_CROSSED") icon = "🔒";

    return `
      <div class="timeline-item">
        <div class="timeline-time">${ev.display_time}</div>
        <div class="timeline-content">
          <div class="timeline-desc">
            <span style="margin-right: 4px;">${icon}</span> ${ev.description}
          </div>
          <div class="timeline-meta">
            <span class="card-badge badge-verified">${ev.verification_status}</span>
            <span>${ev.location_name || 'Home'}</span>
            ${ev.privacy_status === 'BOUNDARY_CROSSED' ? '<span class="card-badge badge-private">Privacy Boundary Crossed</span>' : ''}
          </div>
        </div>
      </div>
    `;
  }).join("");
}
