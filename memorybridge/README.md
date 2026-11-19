# MemoryBridge AI

> **“The environment remembers, so they don’t have to.”**  
> *An External Memory System for Independent Living*

---

## 🏆 Hackathon Overview

**MemoryBridge AI** is a privacy-aware, ambient external memory prototype engineered to assist elderly individuals experiencing cognitive impairment or mild dementia.

Rather than forcing the person who struggles with memory to operate complex mobile apps, wearables, or manual buttons, MemoryBridge leverages ambient spatio-temporal observation to remember important daily events and answer natural questions—**without surveillance, without hallucinated facts, and without diagnostic claims.**

---

## 🏛️ The Five Core Pillars

| Pillar | Principle | Implementation in MemoryBridge |
| :--- | :--- | :--- |
| **1. Observe 👁️** | Selective safe observation | OpenCV vision stream detecting only 5 vital items: Person, Keys, Glasses, Wallet, Medicine container. Real-time visual Privacy Shield active in private rooms. |
| **2. Connect 🧠** | Spatio-temporal event graph | Relational SQLite event ledger linking **WHO + WHAT + WHERE + WHEN + ACTION** with explicit confidence and status (`VERIFIED`, `INFERRED`, `UNCERTAIN`). |
| **3. Anchor ⚓** | Contextual proactive assistance | Informs the resident when a morning action (e.g. medicine interaction) has already been logged. Frames actions honestly (*"container interaction recorded"* rather than claiming physiological ingestion). |
| **4. Recall 🔄** | Grounded natural retrieval | Natural language recall via text & voice (Web Speech STT/TTS). LLM acts as an explanation layer, **never** inventing facts. Unknown items return honest uncertainty. |
| **5. Notice ⚠️** | Routine deviation detection | Compares current trajectory against a multi-week baseline. Detects pacing or omitted anchors. Frames output objectively (*"Observed activity differs significantly from baseline"*) without diagnostic alarmism. |

---

## 🔒 Privacy Architecture & The "Last Confirmed" Principle

Traditional camera solutions turn homes into panopticons. MemoryBridge enforces a **Hardware-Grade Spatial Privacy Firewall**:

- **Activity Zones (Living Room, Kitchen, Dining):** Ambient tracking permitted.
- **Private Zones (Bedroom, Bathroom):** Visual tracking is **instantly severed** at the doorway threshold.

### The Core Invariant:
When an object (e.g., keys) enters a bedroom:
- **GOOD:** *"Your keys were last confirmed entering the bedroom at 2:15 PM."*
- **BAD (Forbidden):** *"Your keys are on the bedroom nightstand drawer."* (The system refuses to fabricate unobserved facts).

---

## ⚡ Quickstart: Running the Prototype

### Prerequisites
- Python 3.10+
- Installed packages: `fastapi`, `uvicorn`, `opencv-python`

### 1. Launch the Server
```bash
python -m uvicorn memorybridge.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Open the Application
Navigate in your browser to:
- **Main Dashboard & Live Home:** [http://localhost:8000/](http://localhost:8000/)
- **Visual Memory Replay:** [http://localhost:8000/replay](http://localhost:8000/replay)
- **My Routine & Deviation Center:** [http://localhost:8000/routine](http://localhost:8000/routine)
- **Privacy Center:** [http://localhost:8000/privacy](http://localhost:8000/privacy)
- **Caregiver Digest:** [http://localhost:8000/caregiver](http://localhost:8000/caregiver)
- **Live Vision Stream:** [http://localhost:8000/camera](http://localhost:8000/camera)

---

## 🎬 6-Step Hackathon Live Presentation Script

Use the top **Demo Toolbar** on the Dashboard for a guaranteed 100% reliable demo:

1. **Step 1 — Simulate Pickup:**  
   Click `[1. Pick up Keys]`.  
   *Result:* Recorded at 2:10 PM on the Living Room table.
2. **Step 2 — Move to Bedroom & Privacy Boundary:**  
   Click `[2. Move to Bedroom]`.  
   *Result:* Keys cross into the Bedroom at 2:15 PM. Visual observation pauses; Privacy Firewall engages.
3. **Step 3 — Grounded Question Answering:**  
   Click `[3. "Where are my keys?"]` (or speak via microphone).  
   *Answer:* *"Your keys were last confirmed entering the bedroom at 2:15 PM."* (Listen via speech synthesis).
4. **Step 4 — Visual Memory Replay:**  
   Click `[4. Replay Memory ▶]`.  
   *Result:* Watch the interactive 2D canvas animate the footsteps from the Living Room coffee table, through the hallway, and stop abruptly at the Bedroom privacy boundary shield.
5. **Step 5 — Routine Deviation Detection:**  
   Click `[5. Routine Deviation ⚠️]`.  
   *Result:* Sequence comparison alerts: *"Observed activity differs significantly from the recent baseline (repeated transit between Bedroom and Hallway)."*
6. **Step 6 — Contextual Medicine Anchor:**  
   Click `[💊 Medicine Anchor]`.  
   *Result:* Proactive banner notifies: *"Your morning medicine interaction was already recorded at 9:00 AM."*

---

## 🧪 Automated Verification

Run the comprehensive offline test suite:

```bash
python memorybridge/test_memorybridge.py
```

All 7 test phases verify database initialization, anchor engine disclaimers, privacy boundary enforcement, grounded recall accuracy, and deviation metrics.

---

## 📁 Project Structure

```text
memorybridge/
├── backend/
│   ├── database.py              # SQLite connection, tables & seeds
│   ├── main.py                  # FastAPI server & static file routing
│   ├── models.py                # Pydantic schemas
│   ├── routes/
│   │   ├── demo.py              # 1-click simulation script scenarios
│   │   ├── events.py            # Event CRUD & contextual anchors
│   │   ├── memory.py            # Natural language recall & replay feeds
│   │   ├── privacy.py           # Privacy zone management & toggles
│   │   ├── routine.py           # Routine baseline & deviation APIs
│   │   └── vision_stream.py     # OpenCV MJPEG streaming with privacy shield
│   └── services/
│       ├── anchor_engine.py     # Proactive medicine assistance
│       ├── event_engine.py      # Spatio-temporal event logger
│       ├── memory_engine.py     # Anti-hallucination recall engine
│       ├── privacy_engine.py    # Privacy boundary rules
│       ├── routine_engine.py    # Baseline sequence comparator
│       └── vision_engine.py     # Camera & synthetic fallback vision
├── frontend/
│   ├── camera.html              # Live OpenCV stream & detection overlay
│   ├── caregiver.html           # Reassuring, filtered caregiver digest
│   ├── index.html               # Main Dashboard with Live Home floorplan
│   ├── privacy.html             # Privacy Center & zone toggles
│   ├── replay.html              # Animated 2D Memory Replay stage
│   ├── routine.html             # Baseline vs Today routine comparator
│   ├── css/
│   │   └── style.css            # Accessible, elderly-friendly design system
│   └── js/
│       ├── api.js               # API client & Web Speech (STT/TTS)
│       ├── caregiver.js         # Caregiver digest controller
│       ├── dashboard.js         # Floorplan & voice query controller
│       ├── privacy.js           # Privacy zone controller
│       ├── replay.js            # Canvas scrubber & animator
│       └── routine.js           # Routine comparison controller
├── test_memorybridge.py         # Automated test suite
└── README.md                    # Project documentation & pitch guide
```
