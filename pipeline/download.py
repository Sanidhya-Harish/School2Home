import os
import re
import requests
from urllib.parse import urlparse


def sanitize_filename(name):
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name


def get_student_folder(student_name):
    folder_name = sanitize_filename(student_name)
    path = os.path.join("data", folder_name)

    if not os.path.exists(path):
        os.makedirs(path)

    return path


def download_pdf(url, file_name, student_name, subject, date, grade):
    # ================== 🔹 NEW CODE START ==================
    subject_lower = subject.lower()
    file_name_lower = file_name.lower()

    if "daily log" in subject_lower:
        grade_patterns = [
            f"gr {grade}".lower(),
            f"grade {grade}".lower(),
            f"g{grade}".lower()
        ]

        if not any(pattern in file_name_lower for pattern in grade_patterns):
            print(f"Skipping Daily Log not matching Grade {grade}: {file_name}")
            return None
    # ================== 🔹 NEW CODE END ==================
    student_folder = get_student_folder(student_name)

    parsed_url = urlparse(url)
    original_filename = os.path.basename(parsed_url.path)

    safe_subject = sanitize_filename(subject)
    safe_date = date.replace("/", "-")

    filename = f"{safe_date}_{safe_subject}_{original_filename}"
    file_path = os.path.join(student_folder, filename)

    if os.path.exists(file_path):
        print(f"Already downloaded: {filename}")
        return file_path

    print(f"Downloading: {filename}")

    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        return file_path
    else:
        print("Download failed:", url)
        return None