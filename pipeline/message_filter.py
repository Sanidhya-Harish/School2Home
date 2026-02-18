import re


def extract_grade_block(text, grade):
    """
    Extract block belonging to specific grade.
    Handles timetable style circulars safely.
    """

    # Look specifically for timetable section
    timetable_pattern = rf"GRADE\s+{grade}\s*[-–]\s*TIMETABLE"

    match = re.search(timetable_pattern, text, re.IGNORECASE)

    if not match:
        return ""

    start = match.start()

    # Find next grade timetable block
    next_match = re.search(r"GRADE\s+\d+\s*[-–]\s*TIMETABLE", text[start + 1:], re.IGNORECASE)

    if next_match:
        end = start + 1 + next_match.start()
        return text[start:end]

    return text[start:]


def section_pattern_exists(text, grade):
    """
    Check if section-specific patterns exist like:
    5A, 5AB, 5ABCDE etc.
    """
    pattern = rf"\b{grade}\s*[A-Z]+\b"
    return re.search(pattern, text) is not None


def filter_by_section(grade_block, grade, section):
    """
    Return only lines matching student section.
    """
    filtered_lines = []
    lines = grade_block.split("\n")

    for line in lines:
        line_clean = line.strip()

        match = re.search(rf"\b{grade}\s*([A-Z]+)\b", line_clean)

        if match:
            section_group = match.group(1)
            if section in section_group:
                filtered_lines.append(line)
        else:
            # Generic line (no section info) → always keep
            filtered_lines.append(line)

    return "\n".join(filtered_lines).strip()


def filter_text_for_student(text, grade, section):
    """
    Main filtering function.

    SAFE FALLBACK MODE:
    - If no grade found → return full text
    - If grade found but no section info → return grade block
    - If section info exists:
        - If section matches → return section-filtered text
        - If section does NOT match → return grade block (safe fallback)
    """

    text_upper = text.upper()

    # 🔹 Detect all grade mentions in document
    found_grades = set()

    # 1️⃣ Match: GRADE 5, GRADE-5, GRADE 5A, GRADE 5ABCDEFG
    pattern_single = r"GRADE[S]?\s*[-]?\s*(\d+)"
    matches_single = re.findall(pattern_single, text_upper)
    found_grades.update(matches_single)

    # 2️⃣ Match: GRADE 1&2 or GRADE 1 & 2
    pattern_and = r"GRADE[S]?\s*(\d+)\s*&\s*(\d+)"
    matches_and = re.findall(pattern_and, text_upper)
    for g1, g2 in matches_and:
        found_grades.add(g1)
        found_grades.add(g2)

    # 3️⃣ Match: GRADES 1 TO 4
    pattern_to = r"GRADE[S]?\s*(\d+)\s*TO\s*(\d+)"
    matches_to = re.findall(pattern_to, text_upper)
    for start, end in matches_to:
        for g in range(int(start), int(end) + 1):
            found_grades.add(str(g))

    # 4️⃣ Match: GRADES 1-4
    pattern_dash = r"GRADE[S]?\s*(\d+)\s*-\s*(\d+)"
    matches_dash = re.findall(pattern_dash, text_upper)
    for start, end in matches_dash:
        for g in range(int(start), int(end) + 1):
            found_grades.add(str(g))

    # 🔹 Case A: No grades mentioned → common circular
    if not found_grades:
        return text.strip()

    # 🔹 Case B: Grades mentioned but student grade not included → ignore
    if grade not in found_grades:
        return ""

    # 🔹 Multi-grade header handling (SAFE VERSION)
    multi_grade_header_pattern = r"GRADE[S]?\s*\d+\s*(&|-|TO)\s*\d+"

    # Only return full text if:
    # - Multi-grade header exists
    # - AND no individual grade timetable blocks exist
    if re.search(multi_grade_header_pattern, text_upper) and \
       not re.search(r"GRADE\s+\d+\s*–\s*TIMETABLE", text_upper):
        return text.strip()

    # 🔹 Step 2: Extract grade block
    grade_block = extract_grade_block(text, grade)

    if not grade_block:
        return text.strip()

    # 🔹 Step 3: Check if section patterns exist
    if not section_pattern_exists(grade_block, grade):
        # No section-level granularity → return whole grade block
        return grade_block.strip()

    # 🔹 Step 4: Filter by section
    filtered = filter_by_section(grade_block, grade, section)

    if filtered:
        return filtered

    # 🔹 SAFE FALLBACK
    return grade_block.strip()
    #return text.strip()

    # ==============================
    # 🔴 OPTION A (STRICT MODE)
    # ==============================
    # Replace SAFE FALLBACK with:
    #
    # return ""
    #
    # If you want strict filtering instead.