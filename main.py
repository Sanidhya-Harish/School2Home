import os
from dotenv import load_dotenv
load_dotenv()
from playwright.sync_api import sync_playwright
#from config import STUDENTS
from scraper.login import login_if_required
from scraper.child_selector import select_child
from scraper.general_scraper import open_general_page, scrape_general_table
from pipeline.download import download_pdf

from llm.extractor import extract_structured_data
from pipeline.pdf_extractor import extract_text_from_pdf
from pipeline.message_filter import filter_text_for_student
from database.supabase_client import supabase
from database.supabase_client import get_students
from database.task_repository import insert_tasks
from database.event_repository import insert_events
from database.exam_repository import insert_exams
from database.circular_repository import (is_circular_processed,mark_circular_processed)
from pipeline.hash_utils import generate_circular_hash
from datetime import datetime, timedelta


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        if os.path.exists("state.json"):
            context = browser.new_context(storage_state="state.json")
        else:
            context = browser.new_context()

        page = context.new_page()

        page.goto("https://gis.pupilpod.net/home.php")
        page.wait_for_load_state("networkidle")

        login_if_required(page, context)

        students = get_students()
        for student in students:
            select_child(page, student["name"])
            open_general_page(page)

            messages = scrape_general_table(page, student)

            for msg in messages:
                for attachment in msg["attachments"]:
                    local_path = download_pdf(
                        attachment["url"],
                        attachment["file_name"],
                        msg["student"],
                        msg["subject"],
                        msg["date"],
                        msg["grade"]
                    )
                    attachment["local_path"] = local_path

                    if local_path:
                        extracted_text = extract_text_from_pdf(local_path)
                        file_name = attachment["file_name"]
                        filtered_text = filter_text_for_student(extracted_text, msg["grade"], msg["section"])
                        combined_text = extracted_text + "\n\n--- GRADE SPECIFIC BLOCK ---\n\n" + filtered_text
                        attachment["extracted_text"] = extracted_text

                        print("Extracted text length:", len(extracted_text))
                        print("Filtered text length:", len(filtered_text))
                        print(filtered_text)

                        # Step 3: Run LLM extraction
                        result = extract_structured_data(combined_text, msg["grade"], msg["section"])

                        # 4️⃣ Dedup + Insert
                        student_id = student["id"]   # ← use dynamic student id
                        #file_name = file_name     # ← use real file name
                        file_size = len(extracted_text)

                        circular_hash = generate_circular_hash(file_name, extracted_text, file_size)

                        if is_circular_processed(student_id, circular_hash):
                            print("⚠ Circular already processed. Skipping insert.")
                        else:
                            insert_tasks(student_id, result.get("tasks", []))
                            insert_events(student_id, result.get("events", []))
                            insert_exams(student_id, result.get("exams", []))

                            mark_circular_processed(student_id, circular_hash)

        browser.close()

def cleanup_old_data():
    cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()

    supabase.table("tasks").delete().lt("created_at", cutoff).execute()

if __name__ == "__main__":
    main()
