from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from backend.models import DemoSimulateRequest
from backend.database import reset_db
from backend.services.event_engine import record_event
from backend.services.privacy_engine import toggle_zone_privacy
from backend.services.vision_engine import vision_service

router = APIRouter(prefix="/api/demo", tags=["demo"])

@router.post("/simulate")
def run_simulation(req: DemoSimulateRequest):
    scenario = req.scenario.lower()
    now = datetime.now()

    if scenario == "key_pickup":
        # Step 1: Keys picked up in Living Room at 2:10 PM
        t1 = now.replace(hour=14, minute=10, second=0)
        ev = record_event(
            user_id="user_01",
            object_id="obj_keys",
            action="picked_up",
            location_id="loc_living_room",
            confidence=0.96,
            verification_status="VERIFIED",
            privacy_status="PUBLIC",
            description="House Keys picked up from living-room coffee table.",
            metadata={"surface": "coffee table", "held_by": "Eleanor Vance"},
            custom_time=t1
        )
        vision_service.set_simulation_target("Keys (Picked up)", "Living Room", 0.96)
        vision_service.set_privacy_mode(False)
        return {
            "status": "success",
            "step": 1,
            "title": "Keys Picked Up",
            "message": "Recorded: House Keys picked up in Living Room at 2:10 PM.",
            "event": ev
        }

    elif scenario == "key_bedroom_move":
        # Step 2: Keys carried through hallway and entered Bedroom at 2:15 PM
        t_transit = now.replace(hour=14, minute=12, second=0)
        ev_transit = record_event(
            user_id="user_01",
            object_id="obj_keys",
            action="carried_through",
            location_id="loc_hallway",
            confidence=0.94,
            verification_status="INFERRED",
            privacy_status="PUBLIC",
            description="Person observed in hallway carrying keys toward bedroom.",
            metadata={"direction": "toward bedroom"},
            custom_time=t_transit
        )

        t2 = now.replace(hour=14, minute=15, second=0)
        ev_bedroom = record_event(
            user_id="user_01",
            object_id="obj_keys",
            action="entered",
            location_id="loc_bedroom",
            confidence=0.92,
            verification_status="VERIFIED",
            privacy_status="BOUNDARY_CROSSED",
            description="House Keys were last confirmed entering the Bedroom at 2:15 PM.",
            metadata={"boundary": "bedroom_threshold", "privacy_shield_engaged": True},
            custom_time=t2
        )
        # Enable privacy firewall
        toggle_zone_privacy("loc_bedroom", 1)
        vision_service.set_privacy_mode(True)
        vision_service.set_simulation_target("Private Zone", "Bedroom", 0.0)

        return {
            "status": "success",
            "step": 2,
            "title": "Bedroom Entry & Privacy Boundary",
            "message": "Recorded: House Keys entered Bedroom at 2:15 PM. Privacy Mode automatically activated.",
            "event": ev_bedroom,
            "transit_event": ev_transit
        }

    elif scenario == "privacy_trigger":
        # Step 3: Explicit visual privacy boundary activation
        toggle_zone_privacy("loc_bedroom", 1)
        vision_service.set_privacy_mode(True)
        return {
            "status": "success",
            "step": 3,
            "title": "Privacy Firewall Engaged",
            "message": "Visual observation disabled in Bedroom. Only non-visual boundary logs permitted."
        }

    elif scenario == "medicine_interaction":
        # Anchor demo: Medicine interaction
        t_med = now.replace(hour=9, minute=0, second=0)
        ev_med = record_event(
            user_id="user_01",
            object_id="obj_medicine",
            action="interacted_with",
            location_id="loc_kitchen",
            confidence=0.95,
            verification_status="VERIFIED",
            privacy_status="PUBLIC",
            description="Morning medicine container interaction recorded at 9:00 AM.",
            metadata={"disclaimer": "Interaction recorded. Physiological consumption cannot be verified."},
            custom_time=t_med
        )
        vision_service.set_simulation_target("Medicine Container", "Kitchen", 0.95)
        return {
            "status": "success",
            "title": "Medicine Interaction Logged",
            "message": "Morning medicine container interaction recorded at 9:00 AM in Kitchen.",
            "event": ev_med
        }

    elif scenario == "routine_deviation":
        # Deviation sequence: Bedroom -> Hallway -> Bedroom -> Hallway -> Bedroom
        t_base = now.replace(hour=8, minute=0, second=0)
        seq = [
            ("loc_bedroom", "entered", "Resident exited bedroom into hallway", 8, 0),
            ("loc_hallway", "entered", "Resident in hallway", 8, 15),
            ("loc_bedroom", "entered", "Resident re-entered bedroom", 8, 18),
            ("loc_hallway", "entered", "Resident paced back to hallway", 8, 25),
            ("loc_bedroom", "entered", "Resident re-entered bedroom again", 8, 30)
        ]
        ev_list = []
        for loc, act, desc, h, m in seq:
            t = now.replace(hour=h, minute=m, second=0)
            ev = record_event(
                user_id="user_01",
                object_id="obj_person",
                action=act,
                location_id=loc,
                confidence=0.93,
                verification_status="VERIFIED",
                privacy_status="ZONE_MASKED" if loc == "loc_bedroom" else "PUBLIC",
                description=desc,
                custom_time=t
            )
            ev_list.append(ev)

        return {
            "status": "success",
            "title": "Routine Deviation Sequence Created",
            "message": "Simulated pacing pattern: Bedroom -> Hallway -> Bedroom -> Hallway -> Bedroom.",
            "events_count": len(ev_list)
        }

    elif scenario == "routine_normal":
        # Normal sequence
        t_base = now.replace(hour=8, minute=0, second=0)
        norm_seq = [
            ("loc_bedroom", "entered", "Resident woke up and exited bedroom", 8, 0, "obj_person"),
            ("loc_kitchen", "entered", "Resident walked into kitchen", 8, 15, "obj_person"),
            ("loc_kitchen", "interacted_with", "Morning medicine container interaction recorded", 8, 20, "obj_medicine"),
            ("loc_dining", "entered", "Breakfast at dining table", 8, 30, "obj_person"),
            ("loc_living_room", "entered", "Resident settled in living room", 8, 50, "obj_person")
        ]
        ev_list = []
        for loc, act, desc, h, m, obj in norm_seq:
            t = now.replace(hour=h, minute=m, second=0)
            ev = record_event(
                user_id="user_01",
                object_id=obj,
                action=act,
                location_id=loc,
                confidence=0.96,
                verification_status="VERIFIED",
                privacy_status="ZONE_MASKED" if loc == "loc_bedroom" else "PUBLIC",
                description=desc,
                custom_time=t
            )
            ev_list.append(ev)

        return {
            "status": "success",
            "title": "Normal Morning Routine Logged",
            "message": "Simulated normal flow: Bedroom -> Kitchen -> Medicine -> Breakfast -> Living Room.",
            "events_count": len(ev_list)
        }

    elif scenario == "reset":
        reset_db()
        vision_service.set_privacy_mode(False)
        vision_service.set_simulation_target("Keys", "Living Room", 0.94)
        return {
            "status": "success",
            "title": "System Reset",
            "message": "MemoryBridge database and privacy firewall reset to fresh baseline."
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unknown scenario '{scenario}'")
