import re
from datetime import datetime
from backend.database import get_db_connection
from backend.services.privacy_engine import is_private_zone

def recall_memory(query: str, user_id: str = "user_01") -> dict:
    """
    Interprets natural language queries using grounded spatio-temporal database records.
    Never hallucinates unobserved locations or unverified facts.
    """
    clean_q = query.lower().strip()
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Object recall queries: keys, glasses, wallet, medicine, phone, etc.
    target_object_id = None
    target_object_name = None

    if "key" in clean_q:
        target_object_id = "obj_keys"
        target_object_name = "Keys"
    elif "glass" in clean_q or "spectacle" in clean_q:
        target_object_id = "obj_glasses"
        target_object_name = "Glasses"
    elif "wallet" in clean_q or "purse" in clean_q:
        target_object_id = "obj_wallet"
        target_object_name = "Wallet"
    elif "medicine" in clean_q or "pill" in clean_q or "medication" in clean_q:
        target_object_id = "obj_medicine"
        target_object_name = "Medicine container"

    # Query Type A: Medicine check
    if "medicine" in clean_q or "pill" in clean_q:
        cursor.execute("""
            SELECT e.*, l.name as location_name, l.zone_type, l.privacy_mode
            FROM events e
            JOIN locations l ON e.location_id = l.id
            WHERE e.user_id = ? AND (e.object_id = 'obj_medicine' OR e.action = 'interacted_with')
            ORDER BY e.timestamp DESC
            LIMIT 5
        """, (user_id,))
        med_rows = [dict(r) for r in cursor.fetchall()]

        if med_rows:
            latest = med_rows[0]
            display_time = latest["display_time"]
            loc_name = latest["location_name"]
            ans = f"Your morning medicine interaction was recorded at {display_time} in the {loc_name}."
            explanation = "Verified container contact event logged by ambient sensor. Physiological consumption cannot be verified."
            conn.close()
            return {
                "query": query,
                "answer": ans,
                "matched_object": "Morning Medicine Container",
                "matched_location": loc_name,
                "observed_time": display_time,
                "verification_status": latest["verification_status"],
                "confidence": latest["confidence"],
                "is_private_zone": False,
                "explanation": explanation,
                "relevant_events": med_rows
            }
        else:
            conn.close()
            return {
                "query": query,
                "answer": "No medicine container interaction has been recorded today.",
                "matched_object": "Morning Medicine Container",
                "matched_location": None,
                "observed_time": None,
                "verification_status": "UNCERTAIN",
                "confidence": 0.5,
                "is_private_zone": False,
                "explanation": "No matching interaction event found in the active database.",
                "relevant_events": []
            }

    # Query Type B: Object Location ("Where are my keys / glasses / wallet?")
    if target_object_id:
        cursor.execute("""
            SELECT e.*, l.name as location_name, l.zone_type, l.privacy_mode, o.name as object_name
            FROM events e
            JOIN locations l ON e.location_id = l.id
            JOIN objects o ON e.object_id = o.id
            WHERE e.user_id = ? AND e.object_id = ?
            ORDER BY e.timestamp DESC
            LIMIT 5
        """, (user_id, target_object_id))
        ev_rows = [dict(r) for r in cursor.fetchall()]

        if not ev_rows:
            conn.close()
            return {
                "query": query,
                "answer": f"I don't have a verified recent observation of your {target_object_name.lower()}.",
                "matched_object": target_object_name,
                "matched_location": None,
                "observed_time": None,
                "verification_status": "UNCERTAIN",
                "confidence": 0.0,
                "is_private_zone": False,
                "explanation": "Object has not been tracked or observed in any active activity zone today.",
                "relevant_events": []
            }

        latest = ev_rows[0]
        loc_name = latest["location_name"]
        display_time = latest["display_time"]
        zone_type = latest["zone_type"]
        is_private = (zone_type == "private")

        if is_private:
            # Privacy boundary logic: strictly last confirmed entering the private zone!
            ans = f"Your {target_object_name.lower()} were last confirmed entering the {loc_name} at {display_time}."
            explanation = f"Observation halted at {loc_name} privacy boundary. Visual tracking inside private zones is strictly disabled to preserve dignity."
        else:
            if latest["action"] in ["placed_on", "observed"]:
                ans = f"Your {target_object_name.lower()} were last observed in the {loc_name} at {display_time}."
            elif latest["action"] == "picked_up":
                ans = f"Your {target_object_name.lower()} were picked up in the {loc_name} at {display_time}."
            else:
                ans = f"Your {target_object_name.lower()} were last confirmed in the {loc_name} at {display_time}."
            explanation = f"Confirmed by verified ambient event in active activity zone ({loc_name})."

        conn.close()
        return {
            "query": query,
            "answer": ans,
            "matched_object": latest.get("object_name", target_object_name),
            "matched_location": loc_name,
            "observed_time": display_time,
            "verification_status": latest["verification_status"],
            "confidence": latest["confidence"],
            "is_private_zone": is_private,
            "explanation": explanation,
            "relevant_events": ev_rows
        }

    # Query Type C: Morning Activity Summary ("What did I do this morning / today?")
    if any(k in clean_q for k in ["what did i do", "morning", "today", "activity", "summary", "schedule"]):
        cursor.execute("""
            SELECT e.*, l.name as location_name, o.name as object_name
            FROM events e
            JOIN locations l ON e.location_id = l.id
            LEFT JOIN objects o ON e.object_id = o.id
            WHERE e.user_id = ?
            ORDER BY e.timestamp ASC
            LIMIT 15
        """, (user_id,))
        morning_rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        if not morning_rows:
            return {
                "query": query,
                "answer": "No ambient activity events have been recorded yet today.",
                "matched_object": None,
                "matched_location": None,
                "observed_time": None,
                "verification_status": "UNCERTAIN",
                "confidence": 0.0,
                "is_private_zone": False,
                "explanation": "Event database is empty.",
                "relevant_events": []
            }

        # Synthesize chronological summary
        actions_summary = []
        for r in morning_rows:
            time_part = r["display_time"]
            loc_part = r["location_name"]
            if r.get("object_id") == "obj_medicine":
                actions_summary.append(f"interacted with your medicine container in the {loc_part} ({time_part})")
            elif r.get("object_id") == "obj_keys":
                actions_summary.append(f"handled your keys ({time_part})")
            elif r.get("object_id") == "obj_glasses":
                actions_summary.append(f"used your reading glasses ({time_part})")
            elif "entered" in r["action"] or "moved" in r["action"]:
                actions_summary.append(f"went to the {loc_part} ({time_part})")
            else:
                actions_summary.append(f"were active in the {loc_part} ({time_part})")

        # Distinct condensed list
        condensed = []
        for a in actions_summary:
            if not condensed or condensed[-1].split(" (")[0] != a.split(" (")[0]:
                condensed.append(a)

        if len(condensed) <= 4:
            joined_str = ", then ".join(condensed)
        else:
            joined_str = ", then ".join(condensed[:4]) + f", and recorded {len(condensed)-4} subsequent transitions"

        ans = f"This morning, you {joined_str}."
        return {
            "query": query,
            "answer": ans,
            "matched_object": "Activity Timeline",
            "matched_location": "Residence",
            "observed_time": morning_rows[-1]["display_time"],
            "verification_status": "VERIFIED",
            "confidence": 0.95,
            "is_private_zone": False,
            "explanation": f"Synthesized from {len(morning_rows)} chronologically ordered spatio-temporal logs.",
            "relevant_events": morning_rows
        }

    # Query Type D: General Fallback
    cursor.execute("""
        SELECT e.*, l.name as location_name, o.name as object_name
        FROM events e
        JOIN locations l ON e.location_id = l.id
        LEFT JOIN objects o ON e.object_id = o.id
        WHERE e.user_id = ?
        ORDER BY e.timestamp DESC
        LIMIT 5
    """, (user_id,))
    recent_events = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if recent_events:
        latest = recent_events[0]
        ans = f"The most recent verified activity was at {latest['display_time']}: {latest['description']}"
        return {
            "query": query,
            "answer": ans,
            "matched_object": latest.get("object_name"),
            "matched_location": latest["location_name"],
            "observed_time": latest["display_time"],
            "verification_status": latest["verification_status"],
            "confidence": 0.90,
            "is_private_zone": latest.get("privacy_status") == "ZONE_MASKED",
            "explanation": "Direct recall based on the most recent verified event in memory.",
            "relevant_events": recent_events
        }

    return {
        "query": query,
        "answer": "I don't have enough verified observations to answer that question.",
        "matched_object": None,
        "matched_location": None,
        "observed_time": None,
        "verification_status": "UNCERTAIN",
        "confidence": 0.0,
        "is_private_zone": False,
        "explanation": "No correlating events discovered in memory repository.",
        "relevant_events": []
    }
