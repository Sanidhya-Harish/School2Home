import json
from datetime import datetime


# Allowed enums (must match DB exactly)
ALLOWED_TASK_TYPES = {"homework", "project", "assignment", "manual"}
ALLOWED_EVENT_TYPES = {"exam", "exhibition", "holiday", "reminder"}


def _safe_date(value):
    """
    Ensure date is either valid YYYY-MM-DD or None.
    """
    if not value:
        return None

    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except Exception:
        return None


def _normalize_string(value):
    """
    Convert empty strings to None.
    """
    if not value or str(value).strip() == "":
        return None
    return str(value).strip()


def validate_llm_output(raw_output):
    """
    Soft validation:
    - Parse JSON safely
    - Normalize enums
    - Clean dates
    - Drop invalid items
    """

    # 🔹 Remove markdown code fences if present
    clean_output = raw_output.strip()

    if clean_output.startswith("```"):
        clean_output = clean_output.strip("`")
        clean_output = clean_output.replace("json", "", 1).strip()

    try:
        data = json.loads(clean_output)
    except Exception:
        print("⚠ Invalid JSON from LLM")
        return {"tasks": [], "events": [], "exams": []}

    cleaned = {
        "tasks": [],
        "events": [],
        "exams": []
    }

    # -------------------
    # Validate Tasks
    # -------------------
    for task in data.get("tasks", []):
        title = _normalize_string(task.get("title"))
        if not title:
            continue  # Title is mandatory

        task_type = _normalize_string(task.get("type"))
        if task_type:
            task_type = task_type.lower()
        if task_type not in ALLOWED_TASK_TYPES:
            task_type = "homework"  # Your rule

        cleaned_task = {
            "title": title,
            "description": _normalize_string(task.get("description")),
            "subject": _normalize_string(task.get("subject")),
            "assigned_date": _safe_date(task.get("assigned_date")),
            "due_date": _safe_date(task.get("due_date")),
            "type": task_type,
        }

        cleaned["tasks"].append(cleaned_task)
    '''
    # -------------------
    # Validate Events
    # -------------------
    for event in data.get("events", []):
        title = _normalize_string(event.get("title"))
        event_date = _safe_date(event.get("event_date"))

        if not title or not event_date:
            continue  # Both required

        event_type = _normalize_string(event.get("type"))
        if event_type:
            event_type = event_type.lower()

        if event_type not in ALLOWED_EVENT_TYPES:
            continue  # Drop invalid event types

        cleaned_event = {
            "title": title,
            "event_date": event_date,
            "type": event_type,
            "description": _normalize_string(event.get("description")),
        }

        cleaned["events"].append(cleaned_event)
    '''
    # -------------------
    # Validate Events
    # -------------------
    for event in data.get("events", []):
        title = _normalize_string(event.get("title"))
        event_date = _safe_date(event.get("event_date"))

        if not title or not event_date:
            continue  # Both required

        event_type = _normalize_string(event.get("type"))
        if event_type:
            event_type = event_type.lower()

        # Skip exams here (handled separately in exams table)
        if event_type == "exam":
            continue

        if event_type not in ALLOWED_EVENT_TYPES:
            continue  # Drop invalid event types

        cleaned_event = {
            "title": title,
            "event_date": event_date,
            "type": event_type,
            "description": _normalize_string(event.get("description")),
        }

        cleaned["events"].append(cleaned_event)
    # -------------------
    # Validate Exams
    # -------------------
    for exam in data.get("exams", []):
        subject = _normalize_string(exam.get("subject"))
        exam_date = _safe_date(exam.get("exam_date"))

        if not subject or not exam_date:
            continue

        portions = exam.get("portions", [])
        if not isinstance(portions, list):
            portions = []

        cleaned_exam = {
            "subject": subject,
            "exam_date": exam_date,
            "portions": [
                _normalize_string(p)
                for p in portions
                if _normalize_string(p)
            ]
        }

        cleaned["exams"].append(cleaned_exam)

    return cleaned