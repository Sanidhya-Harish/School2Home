import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from database.supabase_client import get_students
from database.task_repository import get_tasks_by_student, update_task_status
from database.event_repository import get_events_by_student
from database.exam_repository import (
    get_exams_with_portions,
    update_portion_status
)

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="School2Home",
    layout="wide"
)

# -----------------------
# CUSTOM STYLING
# -----------------------
st.markdown("""
<style>
.main-title {
    font-size: 28px;
    font-weight: 700;
}
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-top: 20px;
}
.card {
    padding: 15px;
    border-radius: 10px;
    background-color: #f8f9fa;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# HEADER
# -----------------------
col1, col2 = st.columns([4,1])

with col1:
    st.markdown('<div class="main-title">📘 School2Home</div>', unsafe_allow_html=True)

with col2:
    students = get_students()
    selected_student = st.selectbox(
        "Select Student",
        students,
        format_func=lambda x: x["name"]
    )

student_id = selected_student["id"]

# -----------------------
# SIDEBAR NAVIGATION
# -----------------------
st.sidebar.title("Navigation")

menu = st.sidebar.radio(
    "",
    [
        "Reminders",
        "Events",
        "Tasks",
        "Exams",
        "Exam Portions",
        "Calendar"
    ]
)

# -----------------------
# CONTENT PANEL
# -----------------------

if menu == "Reminders":
    st.markdown("## 🔔 Reminders")
    st.info("Coming soon — auto reminders from tasks & exams")

# --------------------------------------------------

elif menu == "Events":
    st.markdown("## 📅 Events")

    events = get_events_by_student(student_id)

    if not events:
        st.info("No upcoming events")
    else:
        for event in events:
            with st.container():
                st.markdown(
                    f"""
                    <div class="card">
                        <b>{event['title']}</b><br>
                        📆 {event['event_date']}<br>
                        Type: {event.get('type','')}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# --------------------------------------------------

elif menu == "Tasks":
    st.markdown("## 📝 Tasks")

    tasks = get_tasks_by_student(student_id)

    if not tasks:
        st.info("No pending tasks")
    else:
        for t in tasks:
            current_completed = (t["status"] == "completed")

            col1, col2 = st.columns([0.1, 0.9])

            with col1:
                checked = st.checkbox(
                    "",
                    value=current_completed,
                    key=f"task_{t['id']}"
                )

            with col2:
                st.markdown(f"""
                <div class="card">
                    <b>{t['title']}</b><br>
                    Subject: {t.get('subject','')}<br>
                    Due: {t.get('due_date','')}
                </div>
                """, unsafe_allow_html=True)

            if checked != current_completed:
                update_task_status(t["id"], checked)
                st.rerun()

# --------------------------------------------------

elif menu == "Exams":
    exams = get_exams_with_portions(student_id)

    st.subheader("🎨 Exam Timetable")

    if not exams:
        st.info("No upcoming exams.")
    else:
        exam_rows = []

        for exam in exams:
            exam_rows.append({
                "Subject": exam["subject"],
                "Date": exam["exam_date"]
            })

        st.dataframe(
            exam_rows,
            use_container_width=True,
            hide_index=True
        )
# --------------------------------------------------

elif menu == "Exam Portions":
    st.markdown("## 📚 Exam Portions")

    exams = get_exams_with_portions(student_id)

    if not exams:
        st.info("No exam portions available")
    else:
        for exam in exams:
            st.markdown(f"### {exam['subject']}")

            for portion in exam["portions"]:
                current_completed = portion.get("completed", False)

                checked = st.checkbox(
                    portion["chapter"],
                    value=current_completed,
                    key=f"portion_{portion['id']}"
                )

                if checked != current_completed:
                    update_portion_status(portion["id"], checked)
                    st.rerun()

# --------------------------------------------------

elif menu == "Calendar":
    st.markdown("## 🗓 Calendar Overview")
    st.info("Phase 2: Combined view of tasks, exams & events")