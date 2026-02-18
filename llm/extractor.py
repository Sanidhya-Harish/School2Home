from llm.prompt_builder import build_extraction_prompt
from llm.llm_client import call_llm
from llm.validator import validate_llm_output

import re
from datetime import datetime


def rule_based_exam_detection(text: str):
    """
    Strong deterministic exam detection.
    Detects:
    - Cycle Test
    - Unit Test
    - Mid Term
    - Final Exam
    - Practical exams
    """

    exams = []

    patterns = [
        r"(Cycle\s*Test[-\s]*[IVX0-9]+).*?from\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        r"(ICT\s*practical\s*exams?).*?from\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            exam_name = match.group(1).strip()
            date_str = match.group(2)

            try:
                exam_date = datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")

                exams.append({
                    "subject": exam_name.title(),
                    "exam_date": exam_date,
                    "portions": []
                })

            except:
                continue

    return exams


def normalize_subject(name):
    return name.lower().replace("exam", "").strip()


def merge_exams(llm_exams, rule_exams):

    existing = {
        (normalize_subject(e["subject"]), e["exam_date"])
        for e in llm_exams
    }

    for exam in rule_exams:
        key = (normalize_subject(exam["subject"]), exam["exam_date"])

        if key not in existing:
            llm_exams.append(exam)

    return llm_exams

def extract_structured_data(text: str, grade: str = None, section: str = None) -> dict:
    """
    Full LLM extraction pipeline:
    1. Build prompt
    2. Call LLM
    3. Validate & normalize output
    4. Rule-based exam backup
    5. Return clean structured dict
    """

    if not text or not text.strip():
        return {"tasks": [], "events": [], "exams": []}

    # Step 1: Build prompt
    prompt = build_extraction_prompt(text, grade=grade, section=section)
    # Step 2: Call LLM
    raw_output = call_llm(prompt)

    #temp
    #print("\n--- RAW LLM OUTPUT ---\n")
    #print(raw_output)

    if not raw_output:
        return {"tasks": [], "events": [], "exams": []}

    # Step 3: Validate
    validated_output = validate_llm_output(raw_output)

    # Step 4: Deterministic exam backup
    rule_exams = rule_based_exam_detection(text)
    validated_output["exams"] = merge_exams(
        validated_output.get("exams", []),
        rule_exams
    )

    return validated_output