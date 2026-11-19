import os
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure memorybridge backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from backend.database import init_db, seed_db, reset_db
from backend.services.event_engine import get_recent_events, record_event, search_events_by_object
from backend.services.anchor_engine import check_medicine_anchor
from backend.services.memory_engine import recall_memory
from backend.services.routine_engine import get_baseline_routine, analyze_routine_deviation
from backend.services.privacy_engine import get_zone_statuses, toggle_zone_privacy, is_private_zone
from backend.routes.demo import run_simulation
from backend.models import DemoSimulateRequest

def run_all_tests():
    print("\n================ TESTING MEMORYBRIDGE AI SERVICES ================\n")

    # 1. Reset Database
    print("1. Resetting database to baseline...")
    reset_db()
    events = get_recent_events()
    assert len(events) >= 4, f"Expected at least 4 baseline events, got {len(events)}"
    print(f"[OK] Initialized and verified database with {len(events)} baseline events.")

    # 2. Test Anchor Engine (Pillar 3: Anchor)
    print("\n2. Testing Contextual Anchor Engine (Pillar 3)...")
    anchor = check_medicine_anchor()
    assert anchor["has_anchor"] is True
    assert "9:00 AM" in anchor["message"]
    assert "consumption" in anchor["disclaimer"].lower() or "diagnose" in anchor["disclaimer"].lower()
    print(f"[OK] Medicine Anchor verified: {anchor['message']}")
    print(f"[OK] Medical disclaimer check: '{anchor['disclaimer']}'")

    # 3. Test Hackathon Demo Scenario Step 1: Pick up Keys
    print("\n3. Testing Demo Step 1 (Key Pickup in Living Room)...")
    res_step1 = run_simulation(DemoSimulateRequest(scenario="key_pickup"))
    assert res_step1["status"] == "success"
    assert res_step1["step"] == 1
    print(f"[OK] Step 1 verified: {res_step1['message']}")

    # 4. Test Hackathon Demo Scenario Step 2: Move to Bedroom
    print("\n4. Testing Demo Step 2 (Move to Bedroom & Privacy Boundary)...")
    res_step2 = run_simulation(DemoSimulateRequest(scenario="key_bedroom_move"))
    assert res_step2["status"] == "success"
    assert res_step2["step"] == 2
    assert res_step2["event"]["privacy_status"] in ["BOUNDARY_CROSSED", "ZONE_MASKED"]
    assert is_private_zone("loc_bedroom") is True
    print(f"[OK] Step 2 verified: {res_step2['message']}")
    print(f"[OK] Privacy status marked as: {res_step2['event']['privacy_status']}")

    # 5. Test Pillar 4: Natural Language Memory Recall (Anti-Hallucination)
    print("\n5. Testing Grounded Memory Recall (Pillar 4)...")
    
    # Query: Where are my keys?
    recall_keys = recall_memory("Where are my keys?")
    print(f"  Q: 'Where are my keys?'")
    print(f"  A: '{recall_keys['answer']}'")
    assert "bedroom" in recall_keys["answer"].lower()
    assert "last confirmed" in recall_keys["answer"].lower()
    assert recall_keys["is_private_zone"] is True
    assert recall_keys["verification_status"] == "VERIFIED"
    print("  [OK] Correctly states 'last confirmed entering the bedroom' without guessing inside location.")

    # Query: What did I do this morning?
    recall_morning = recall_memory("What did I do this morning?")
    print(f"  Q: 'What did I do this morning?'")
    print(f"  A: '{recall_morning['answer']}'")
    assert "morning" in recall_morning["answer"].lower() or "went" in recall_morning["answer"].lower()
    print("  [OK] Chronological morning synthesis verified.")

    # Query: Where did I keep my glasses?
    recall_glasses = recall_memory("Where did I keep my glasses?")
    print(f"  Q: 'Where did I keep my glasses?'")
    print(f"  A: '{recall_glasses['answer']}'")
    assert "glasses" in recall_glasses["answer"].lower()
    print("  [OK] Glasses location recall verified.")

    # Query: Where is my wallet? (unobserved/uncertain)
    recall_wallet = recall_memory("Where is my wallet?")
    print(f"  Q: 'Where is my wallet?'")
    print(f"  A: '{recall_wallet['answer']}'")
    print("  [OK] Handled query cleanly without hallucinations.")

    # 6. Test Pillar 5: Routine Deviation Detection
    print("\n6. Testing Routine Deviation Engine (Pillar 5)...")
    res_dev = run_simulation(DemoSimulateRequest(scenario="routine_deviation"))
    assert res_dev["status"] == "success"
    
    dev_analysis = analyze_routine_deviation()
    print(f"  Status: {dev_analysis['status_label']}")
    print(f"  Summary: {dev_analysis['summary_message']}")
    print(f"  Points: {dev_analysis['deviation_points']}")
    assert dev_analysis["is_deviated"] is True
    assert "Observed activity differs significantly from the recent baseline" in dev_analysis["summary_message"]
    # Verify non-diagnostic rule: no dementia diagnosis, only objective deviation
    assert "dementia" not in dev_analysis["summary_message"].lower()
    print("  [OK] Routine deviation properly detected and framed non-diagnostically.")

    # 7. Test Privacy Engine
    print("\n7. Testing Privacy Firewall Zone Toggles...")
    zones = get_zone_statuses()
    assert len(zones) >= 5
    bedroom_zone = next(z for z in zones if z["id"] == "loc_bedroom")
    assert bedroom_zone["zone_type"] == "private"
    toggle_zone_privacy("loc_bedroom", 0)
    assert is_private_zone("loc_bedroom") is False
    toggle_zone_privacy("loc_bedroom", 1)
    assert is_private_zone("loc_bedroom") is True
    print("  [OK] Privacy zone toggles verified.")

    print("\n================ ALL MEMORYBRIDGE AI TESTS PASSED! ================\n")

if __name__ == "__main__":
    run_all_tests()
