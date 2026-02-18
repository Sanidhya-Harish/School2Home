import os
import streamlit as st

def get_secret(key):
    try:
        return st.secrets[key]  # Streamlit Cloud
    except Exception:
        return os.getenv(key)   # Local .env or GitHub Actions


USERNAME = get_secret("USERNAME")
PASSWORD = get_secret("PASSWORD")

IGNORE_KEYWORDS = ["newsletter", "menu"]

GROQ_API_KEY = get_secret("GROQ_API_KEY")
SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")