/**
 * MemoryBridge AI — Privacy Center Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  loadZones();
});

async function loadZones() {
  try {
    const zones = await API.getPrivacyZones();
    renderZones(zones);
  } catch (err) {
    console.error("Failed to load privacy zones:", err);
  }
}

function renderZones(zones) {
  const container = document.getElementById("privacy-zones-grid");
  if (!container) return;

  container.innerHTML = zones.map(z => {
    const isPrivate = z.zone_type === "private";
    const isActive = z.privacy_mode === 1;

    return `
      <div class="zone-card ${isPrivate ? 'private-zone' : 'activity-zone'}">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
            <h4 style="font-size:1.05rem; font-weight:700; color:#1e293b;">
              ${isPrivate ? '🔒' : '👁️'} ${z.name}
            </h4>
            <span class="card-badge ${isPrivate ? 'badge-private' : 'badge-activity'}">
              ${isPrivate ? 'Strict Private Zone' : 'Activity Zone'}
            </span>
          </div>
          <p style="font-size:0.85rem; color:#64748b; margin-bottom:1rem;">
            ${z.description || ''}
          </p>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #f1f5f9; padding-top:0.75rem;">
          <span style="font-size:0.82rem; font-weight:700; color:${isActive ? '#7c3aed' : '#059669'};">
            ${isActive ? 'Shield Active' : 'Observation Active'}
          </span>
          <label class="toggle-switch">
            <input 
              type="checkbox" 
              ${isActive ? 'checked' : ''} 
              onchange="handleToggle('${z.id}', this.checked)"
            />
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
    `;
  }).join("");
}

async function handleToggle(zoneId, isChecked) {
  const mode = isChecked ? 1 : 0;
  try {
    await API.togglePrivacyZone(zoneId, mode);
    showToast(`Updated privacy settings for ${zoneId}.`, "success");
    loadZones();
  } catch (err) {
    console.error(err);
    showToast("Failed to toggle privacy zone.", "danger");
  }
}

async function triggerPrivacyTest() {
  const output = document.getElementById("privacy-test-output");
  output.innerHTML = `<em>Simulating transit across Bedroom threshold...</em>`;

  try {
    const res = await API.runDemoSimulation("key_bedroom_move");
    output.innerHTML = `
      <strong style="color:#7e22ce;">🔒 Privacy Firewall Triggered!</strong><br>
      ${res.message}<br>
      <span style="font-size:0.78rem; color:#64748b;">Event ID: ${res.event.id} | Status: ${res.event.privacy_status}</span>
    `;
    showToast("Bedroom Privacy Firewall engaged!", "success");
    loadZones();
  } catch (err) {
    output.innerText = "Error: " + err.message;
  }
}
