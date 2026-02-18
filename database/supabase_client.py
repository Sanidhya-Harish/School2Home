from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_students():
    response = supabase.table("students").select("*").execute()
    return response.data