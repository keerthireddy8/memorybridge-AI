/**
 * MemoryBridge AI — API Client & Accessibility Speech Utilities
 */

const API = {
  baseUrl: "",

  async getEvents(limit = 25) {
    const res = await fetch(`${this.baseUrl}/api/events?limit=${limit}`);
    return await res.json();
  },

  async askMemory(query) {
    const res = await fetch(`${this.baseUrl}/api/memory/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    return await res.json();
  },

  async getReplaySequence() {
    const res = await fetch(`${this.baseUrl}/api/memory/replay`);
    return await res.json();
  },

  async getRoutineBaseline() {
    const res = await fetch(`${this.baseUrl}/api/routine/baseline`);
    return await res.json();
  },

  async getRoutineDeviation() {
    const res = await fetch(`${this.baseUrl}/api/routine/deviation`);
    return await res.json();
  },

  async getMedicineAnchor() {
    const res = await fetch(`${this.baseUrl}/api/events/anchor/medicine`);
    return await res.json();
  },

  async getPrivacyZones() {
    const res = await fetch(`${this.baseUrl}/api/privacy/zones`);
    return await res.json();
  },

  async togglePrivacyZone(locationId, privacyMode) {
    const res = await fetch(`${this.baseUrl}/api/privacy/zones/${locationId}/toggle`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ privacy_mode: privacyMode })
    });
    return await res.json();
  },

  async runDemoSimulation(scenario) {
    const res = await fetch(`${this.baseUrl}/api/demo/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario })
    });
    return await res.json();
  }
};

// ================= Accessibility Voice Utilities =================

/**
 * Clean, natural Text-to-Speech using browser SpeechSynthesis
 */
function speakText(text) {
  if (!("speechSynthesis" in window)) {
    showToast("Speech synthesis is not supported in this browser.");
    return;
  }
  window.speechSynthesis.cancel(); // Stop any active speech
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95; // Slightly slower, calm cadence for elderly comprehension
  utterance.pitch = 1.0;
  window.speechSynthesis.speak(utterance);
}

/**
 * Speech Recognition for natural question input
 */
function createSpeechRecognizer(onResult, onEnd, onError) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    return null;
  }
  const recognizer = new SpeechRecognition();
  recognizer.continuous = false;
  recognizer.interimResults = false;
  recognizer.lang = "en-US";

  recognizer.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    if (onResult) onResult(transcript);
  };

  recognizer.onerror = (event) => {
    if (onError) onError(event.error);
  };

  recognizer.onend = () => {
    if (onEnd) onEnd();
  };

  return recognizer;
}

// ================= UI Notifications =================
function showToast(message, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>🔔</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
