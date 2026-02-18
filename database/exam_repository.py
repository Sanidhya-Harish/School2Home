from database.supabase_client import supabase


def insert_exams(student_id, exams):

    if not exams:
        print("No exams to insert")
        return

    for exam in exams:

        try:
            exam_row = {
                "student_id": student_id,
                "subject": exam.get("subject"),
                "exam_date": exam.get("exam_date"),
                "exam_type": "cycle_test"
            }

            exam_response = supabase.table("exams").insert(exam_row).execute()

            exam_id = exam_response.data[0]["id"]

            portions = exam.get("portions", [])

            portion_rows = []
            for chapter in portions:
                portion_rows.append({
                    "exam_id": exam_id,
                    "chapter": chapter
                })

            if portion_rows:
                supabase.table("exam_portions").insert(portion_rows).execute()

        except Exception as e:
            print("Error inserting exam:", e)

    print("Inserted exams and portions")

def get_exams_with_portions(student_id: str):
    exams_response = (
        supabase.table("exams")
        .select("*")
        .eq("student_id", student_id)
        .execute()
    )

    exams = exams_response.data

    for exam in exams:
        portions_response = (
            supabase.table("exam_portions")
            .select("*")
            .eq("exam_id", exam["id"])
            .execute()
        )

        exam["portions"] = portions_response.data

    return exams

def update_portion_status(portion_id: str, completed: bool):
    return (
        supabase.table("exam_portions")
        .update({"completed": completed})
        .eq("id", portion_id)
        .execute()
    )