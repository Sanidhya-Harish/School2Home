from database.supabase_client import supabase


def is_circular_processed(student_id, circular_hash):
    try:
        response = (
            supabase.table("processed_circulars")
            .select("*")
            .eq("student_id", student_id)
            .eq("circular_hash", circular_hash)
            .execute()
        )

        return len(response.data) > 0

    except Exception as e:
        print("Error checking circular:", e)
        return False


def mark_circular_processed(student_id, circular_hash):
    try:
        response = (
            supabase.table("processed_circulars")
            .insert({
                "student_id": student_id,
                "circular_hash": circular_hash
            })
            .execute()
        )

        print("Marked circular as processed")

    except Exception as e:
        print("Error marking circular:", e)