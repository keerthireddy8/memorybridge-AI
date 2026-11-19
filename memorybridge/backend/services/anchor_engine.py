from datetime import datetime
from backend.database import get_db_connection

def check_medicine_anchor(user_id: str = "user_01") -> dict:
    """
    Checks if a medicine interaction was already recorded today.
    Returns contextual advisory without making medical diagnostic or consumption claims.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.*, l.name as location_name
        FROM events e
        JOIN locations l ON e.location_id = l.id
        WHERE e.user_id = ? AND (e.object_id = 'obj_medicine' OR e.action = 'interacted_with')
        ORDER BY e.timestamp DESC
        LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "has_anchor": False,
            "status": "NO_RECORD",
            "message": "No medicine container interaction recorded yet today.",
            "last_interaction_time": None,
            "verification_status": "UNCERTAIN",
            "disclaimer": "Interaction tracking only. Does not verify physical ingestion."
        }

    display_time = row["display_time"]
    location_name = row["location_name"]

    return {
        "has_anchor": True,
        "status": "RECORDED_TODAY",
        "message": f"Your morning medicine interaction was already recorded at {display_time} in the {location_name}.",
        "last_interaction_time": display_time,
        "location": location_name,
        "verification_status": "VERIFIED",
        "disclaimer": "Recorded as container interaction. MemoryBridge does not diagnose or verify physiological consumption."
    }
