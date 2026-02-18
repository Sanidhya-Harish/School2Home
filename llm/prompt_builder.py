from datetime import datetime


def build_extraction_prompt(text, grade=None, section=None):
    """
    Build strict structured extraction prompt for academic circulars.
    """

    today = datetime.today().strftime("%Y-%m-%d")

    context_block = ""

    if grade:
        context_block += f"\nTarget Grade: {grade}"

    if section:
        context_block += f"\nTarget Section: {section}"

    prompt = f"""
You are an academic information extraction engine.

Your task:
Extract structured academic data from the provided text.

Today’s date: {today}
{context_block}

CRITICAL RULES:
- Return STRICT JSON only.
- No markdown.
- No explanation.
- No comments.
- Do not invent data.
- Extract only information clearly present in the text.

JSON FORMAT:

{{
  "tasks": [
    {{
      "title": "",
      "description": "",
      "subject": "",
      "assigned_date": "",
      "due_date": "",
      "type": ""
    }}
  ],
  "events": [
    {{
      "title": "",
      "event_date": "",
      "type": "",
      "description": ""
    }}
  ],
  "exams": [
    {{
      "subject": "",
      "exam_date": "",
      "portions": []
    }}
  ]
}}

ENUM RULES:

Task type must be one of:
- homework
- project
- assignment
- manual

Event type must be one of:
- exam
- exhibition
- holiday
- reminder

DATE RULES:
- All dates must be in YYYY-MM-DD format.
- If date is missing, use empty string "".

EXTRACTION RULES:

TASKS:
- Include homework, assignments, projects, submissions.
- Include actionable items only.

EVENTS:
- Include exhibitions, holidays, reminders.
- Include general school events.

EXAMS:
- Include subject, exam date, and portions if mentioned.
- Do not create study tasks automatically.

EXAM EXTRACTION RULES:
If circular mentions:
   - "Test"
   - "Exam"
   - "Cycle Test"
   - "Unit Test"
   - "Mid Term"
   - "Final Exam"

   AND has a specific date or date range

   → Always extract it under "exams"

2. If date range exists:
   Use the START DATE as exam_date.
3. Do NOT convert exams into tasks.
4. ICT practical exams are also exams.
5. English Handwriting Competition is NOT an exam.
6. If the text contains:
   - The word "TIMETABLE"
   - OR multiple subjects listed with dates in sequence
   - OR a structured schedule format like:
        DATE + SUBJECT followed by portions

   Then treat it as an EXAM schedule, not homework.

7. When subjects are listed under specific dates with portions,
   extract each subject-date combination as a separate exam entry.

8. Do NOT classify exam timetable portions as homework or assignments.

If no items exist in a category, return an empty list.

TEXT:
{text}
"""

    return prompt