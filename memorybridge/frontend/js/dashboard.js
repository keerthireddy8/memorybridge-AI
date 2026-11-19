/**
 * MemoryBridge AI — Dashboard Controller
 */

let speechRecognizer = null;
let isListening = false;
let latestAnswerText = "";

document.addEventListener("DOMContentLoaded", () => {
  loadEvents();
  loadMedicineAnchor();
  setupSpeechRecognition();

  // Polling every 5 seconds for live ambient updates
  setInterval(() => {
    loadEvents();
    loadMedicineAnchor();
  }, 5000);
});

// ================= Load Events & Update Floorplan =================
async function loadEvents() {
  try {
    const events = await API.getEvents(20);
    renderTimeline(events);
    updateFloorplan(events);
  } catch (err) {
    console.error("Failed to load events:", err);
  }
}

function renderTimeline(events) {
  const container = document.getElementById("timeline-list");
  if (!container) return;

  if (!events || events.length === 0) {
    container.innerHTML = `<div style="text-align: center; color: #94a3b8; padding: 2rem;">No events recorded yet.</div>`;
    return;
  }

  container.innerHTML = events.map(ev => {
    let badgeClass = "badge-verified";
    if (ev.verification_status === "INFERRED") badgeClass = "badge-inferred";
    if (ev.verification_status === "UNCERTAIN") badgeClass = "badge-uncertain";

    let icon = "📍";
    if (ev.object_id === "obj_keys") icon = "🔑";
    else if (ev.object_id === "obj_glasses") icon = "👓";
    else if (ev.object_id === "obj_medicine") icon = "💊";
    else if (ev.object_id === "obj_wallet") icon = "👛";
    else if (ev.object_id === "obj_person") icon = "👤";

    const isPrivacyBoundary = ev.privacy_status === "BOUNDARY_CROSSED" || ev.privacy_status === "ZONE_MASKED";

    return `
      <div class="timeline-item">
        <div class="timeline-time">${ev.display_time}</div>
        <div class="timeline-content">
          <div class="timeline-desc">
            <span style="margin-right: 4px;">${icon}</span> ${ev.description}
          </div>
          <div class="timeline-meta">
            <span class="card-badge ${badgeClass}">${ev.verification_status}</span>
            <span>in ${ev.location_name || 'Home'}</span>
            ${isPrivacyBoundary ? '<span class="card-badge badge-private" style="margin-left:4px;">🔒 Privacy Boundary</span>' : ''}
          </div>
        </div>
      </div>
    `;
  }).join("");
}

function updateFloorplan(events) {
  if (!events || events.length === 0) return;

  // Find latest locations of keys and resident
  const keyEvent = events.find(e => e.object_id === "obj_keys");
  const keysMarker = document.getElementById("marker-keys");
  const livingRoomZone = document.querySelector("#zone-living-room .room-interior");
  const bedroomZone = document.querySelector("#zone-bedroom .room-interior");

  if (keysMarker && keyEvent) {
    if (keyEvent.location_id === "loc_bedroom") {
      // In private zone: show privacy shield message
      keysMarker.remove();
      const bedroomContent = document.getElementById("bedroom-interior-content");
      if (bedroomContent) {
        bedroomContent.innerHTML = `
          <div style="text-align: center;">
            <div class="entity-item" style="background:#fae8ff; border-color:#c084fc; color:#7e22ce;">
              <span>🔑</span> Keys (Boundary Crossed)
            </div>
            <div style="font-size: 0.72rem; color: #a855f7; margin-top: 4px; font-weight:700;">
              Visual observation paused
            </div>
          </div>
        `;
      }
    } else {
      // Keys in Living Room
      if (!document.getElementById("marker-keys")) {
        const span = document.createElement("div");
        span.id = "marker-keys";
        span.className = "entity-item";
        span.innerHTML = "<span>🔑</span> Keys";
        livingRoomZone.appendChild(span);
      }
    }
  }
}

// ================= Pillar 3: Contextual Anchor =================
async function loadMedicineAnchor() {
  try {
    const anchor = await API.getMedicineAnchor();
    const banner = document.getElementById("anchor-banner");
    if (!banner) return;

    if (anchor && anchor.has_anchor) {
      banner.style.display = "flex";
      document.getElementById("anchor-title").innerText = "Contextual Anchor: Morning Medicine Recorded";
      document.getElementById("anchor-message").innerText = anchor.message;
      document.getElementById("anchor-disclaimer").innerText = anchor.disclaimer;
    } else {
      banner.style.display = "none";
    }
  } catch (err) {
    console.error("Failed to load medicine anchor:", err);
  }
}

// ================= Pillar 4: Ask Memory Recall =================
async function handleAskMemory(e) {
  if (e) e.preventDefault();
  const input = document.getElementById("ask-query-input");
  const query = input.value.trim();
  if (!query) return;

  await performAskMemory(query);
}

function setQueryAndSubmit(text) {
  const input = document.getElementById("ask-query-input");
  if (input) {
    input.value = text;
    performAskMemory(text);
  }
}

async function performAskMemory(query) {
  const answerBox = document.getElementById("answer-box");
  const answerText = document.getElementById("answer-text");
  const answerStatus = document.getElementById("answer-status-badge");
  const answerConf = document.getElementById("answer-confidence-badge");
  const answerExp = document.getElementById("answer-explanation");

  answerBox.style.display = "block";
  answerText.innerText = "Recalling verified memories from database...";

  try {
    const res = await API.askMemory(query);
    latestAnswerText = res.answer;

    answerText.innerText = `"${res.answer}"`;
    answerStatus.innerText = res.verification_status;
    answerStatus.className = `card-badge ${
      res.verification_status === 'VERIFIED' ? 'badge-verified' :
      res.verification_status === 'INFERRED' ? 'badge-inferred' : 'badge-uncertain'
    }`;
    answerConf.innerText = `${Math.round(res.confidence * 100)}% Confidence`;
    answerExp.innerText = `Grounding: ${res.explanation}`;

    // Auto speak answer for elderly accessibility
    speakText(res.answer);
  } catch (err) {
    console.error("Ask memory error:", err);
    answerText.innerText = "Unable to retrieve memory records.";
    answerStatus.innerText = "ERROR";
  }
}

function readAnswerAloud() {
  if (latestAnswerText) {
    speakText(latestAnswerText);
  }
}

// ================= Speech Recognition =================
function setupSpeechRecognition() {
  const micBtn = document.getElementById("voice-mic-btn");
  if (!micBtn) return;

  speechRecognizer = createSpeechRecognizer(
    (transcript) => {
      const input = document.getElementById("ask-query-input");
      if (input) {
        input.value = transcript;
        performAskMemory(transcript);
      }
    },
    () => {
      isListening = false;
      micBtn.classList.remove("listening");
    },
    (err) => {
      console.warn("Speech recognition error:", err);
      showToast("Speech recognition stopped or unavailable.");
      isListening = false;
      micBtn.classList.remove("listening");
    }
  );

  if (!speechRecognizer) {
    micBtn.title = "Speech recognition not supported in this browser";
  }
}

function toggleVoiceInput() {
  if (!speechRecognizer) {
    showToast("Voice input is not supported in this browser. Please type your query.");
    return;
  }
  const micBtn = document.getElementById("voice-mic-btn");
  if (isListening) {
    speechRecognizer.stop();
    isListening = false;
    micBtn.classList.remove("listening");
  } else {
    try {
      speechRecognizer.start();
      isListening = true;
      micBtn.classList.add("listening");
      showToast("Listening... speak your question.");
    } catch (e) {
      console.error(e);
    }
  }
}

// ================= Hackathon 1-Click Demo Steps =================
async function triggerDemoStep(step) {
  if (step === "ask_keys") {
    setQueryAndSubmit("Where are my keys?");
    return;
  }

  showToast(`Executing demo step: ${step.replace('_', ' ')}...`);
  try {
    const res = await API.runDemoSimulation(step);
    showToast(res.message || "Step executed successfully!", "success");
    await loadEvents();
    await loadMedicineAnchor();

    if (step === "key_bedroom_move") {
      document.getElementById("nav-privacy-status").innerText = "🔒 Privacy Shield ENGAGED";
    } else if (step === "reset") {
      document.getElementById("nav-privacy-status").innerText = "🔒 Privacy Firewall ON";
      document.getElementById("ask-query-input").value = "";
      document.getElementById("answer-box").style.display = "none";
    }
  } catch (err) {
    console.error("Demo step execution failed:", err);
    showToast("Simulation step failed: " + err.message, "danger");
  }
}
