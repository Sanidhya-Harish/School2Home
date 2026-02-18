from database.supabase_client import supabase


def insert_tasks(student_id, tasks):

    if not tasks:
        print("No tasks to insert")
        return

    rows = []

    for task in tasks:
        rows.append({
            "student_id": student_id,
            "title": task.get("title"),
            "description": task.get("description"),
            "subject": task.get("subject"),
            "assigned_date": task.get("assigned_date"),
            "due_date": task.get("due_date"),
            "type": task.get("type"),
            "source": "llm",
            "status": "pending",
            "archived": False
        })

    try:
        response = supabase.table("tasks").insert(rows).execute()
        print(f"Inserted {len(response.data)} tasks")
    except Exception as e:
        print("Error inserting tasks:", e)

def update_task_status(task_id: str, completed: bool):
    new_status = "completed" if completed else "pending"

    return (
        supabase.table("tasks")
        .update({"status": new_status})
        .eq("id", task_id)
        .execute()
    )

def get_tasks_by_student(student_id: str):
    response = (
        supabase.table("tasks")
        .select("*")
        .eq("student_id", student_id)
        .eq("archived", False)
        .order("due_date", desc=False)
        .execute()
    )

    return response.data