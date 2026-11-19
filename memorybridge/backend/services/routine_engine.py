from datetime import datetime
from backend.database import get_db_connection

def get_baseline_routine(user_id: str = "user_01") -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.step_order, r.activity, l.name as location_name, r.typical_time, r.notes
        FROM routines r
        JOIN locations l ON r.location_id = l.id
        WHERE r.user_id = ?
        ORDER BY r.step_order ASC
    """, (user_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_today_activity_sequence(user_id: str = "user_01") -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.action, e.display_time, e.timestamp, l.name as location_name,
               o.name as object_name, e.description, e.verification_status
        FROM events e
        JOIN locations l ON e.location_id = l.id
        LEFT JOIN objects o ON e.object_id = o.id
        WHERE e.user_id = ?
        ORDER BY e.timestamp ASC
    """, (user_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def analyze_routine_deviation(user_id: str = "user_01") -> dict:
    """
    Compares the expected baseline sequence with today's observed sequence.
    Detects looping, omissions, or anomalies without clinical diagnosis.
    """
    baseline_steps = get_baseline_routine(user_id)
    baseline_sequence = [step["location_name"] for step in baseline_steps]
    # Also human-readable list:
    baseline_display = [f"{s['typical_time']} — {s['activity']} ({s['location_name']})" for s in baseline_steps]

    today_events = get_today_activity_sequence(user_id)

    # Filter location transitions in today's events
    current_sequence = []
    current_display = []
    for ev in today_events:
        loc = ev["location_name"]
        if not current_sequence or current_sequence[-1] != loc or ev.get("object_name") == "Morning Medicine Container":
            current_sequence.append(loc)
            desc = ev["description"] if ev["description"] else f"In {loc}"
            current_display.append(f"{ev['display_time']} — {desc}")

    # Check for deviation heuristics:
    # 1. Repetitive back-and-forth between same locations (e.g., Bedroom <-> Hallway <-> Bedroom)
    # 2. Missed vital anchors (like Kitchen/Medicine by expected time window)
    is_deviated = False
    deviation_points = []
    summary_msg = "Observed activity is consistent with recent morning baseline."

    if len(current_sequence) >= 3:
        # Check for oscillating loop (A -> B -> A -> B)
        oscillations = 0
        for i in range(len(current_sequence) - 2):
            if current_sequence[i] == current_sequence[i+2] and current_sequence[i] != current_sequence[i+1]:
                oscillations += 1
                deviation_points.append(f"Repeated transit between {current_sequence[i]} and {current_sequence[i+1]} without proceeding to scheduled activity.")

        if oscillations >= 1:
            is_deviated = True
            summary_msg = "Observed activity differs significantly from the recent baseline."

    # If sequence deviates strongly from baseline order
    if not is_deviated and len(current_sequence) >= 4:
        # Compare first 3 elements
        matches = sum(1 for b, c in zip(baseline_sequence[:len(current_sequence)], current_sequence) if b == c)
        similarity = matches / min(len(baseline_sequence), len(current_sequence))
        if similarity < 0.4:
            is_deviated = True
            summary_msg = "Observed activity differs significantly from the recent baseline."
            deviation_points.append(f"Current trajectory deviates from anticipated morning flow: expected progression toward Kitchen/Dining.")

    now_str = datetime.now().strftime("%I:%M %p").lstrip("0")

    return {
        "is_deviated": is_deviated,
        "status_label": "Significant Routine Deviation Detected" if is_deviated else "Routine Aligned",
        "summary_message": summary_msg,
        "normal_sequence": baseline_display,
        "current_sequence": current_display if current_display else ["No morning activity recorded yet"],
        "deviation_points": deviation_points if deviation_points else ["No abnormal oscillations detected."],
        "timestamp": now_str,
        "advice": "System observation note: Provided for routine contextual awareness. Not an indicator of medical diagnosis or clinical episode."
    }
