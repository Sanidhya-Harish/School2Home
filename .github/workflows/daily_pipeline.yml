import os
from datetime import datetime, timedelta
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def cleanup_old_notifications():
    seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()

    response = supabase.table("notifications") \
        .delete() \
        .lt("created_at", seven_days_ago) \
        .execute()

    print("Cleanup complete:", response)

if __name__ == "__main__":
    cleanup_old_notifications()