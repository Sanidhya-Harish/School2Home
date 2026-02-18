from database.supabase_client import supabase


def insert_events(student_id, events):
    if not events:
        print("No events to insert")
        return

    rows = []

    for event in events:
        rows.append({
            "student_id": student_id,
            "title": event.get("title"),
            "description": event.get("description"),
            "event_date": event.get("event_date"),
            "type": event.get("type")
        })

    try:
        response = supabase.table("events").insert(rows).execute()
        print(f"Inserted {len(response.data)} events")
    except Exception as e:
        print("Error inserting events:", e)

def get_events_by_student(student_id: str):
    response = (
        supabase.table("events")
        .select("*")
        .eq("student_id", student_id)
        .order("event_date", desc=False)
        .execute()
    )
    return response.data