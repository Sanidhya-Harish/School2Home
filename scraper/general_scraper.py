from config import IGNORE_KEYWORDS

def open_general_page(page):
    general_url = (
        "https://gis.pupilpod.net/index.php?q="
        "/modules/Messenger/messageWall_view_new.php&category=General"
    )

    page.goto(general_url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(5000)

    print("Now at:", page.url)


def should_ignore(subject):
    subject_lower = subject.lower()
    return any(keyword in subject_lower for keyword in IGNORE_KEYWORDS)


def scrape_general_table(page, student_config):
    print(f"\nScraping messages for {student_config['name']}...")

    page.wait_for_selector("table")

    rows = page.locator("table tbody tr")
    row_count = rows.count()

    print("Total messages found:", row_count)

    messages = []

    for i in range(row_count):
        row = rows.nth(i)
        columns = row.locator("td")

        if columns.count() >= 5:
            student = columns.nth(1).inner_text().strip()
            date = columns.nth(2).inner_text().strip()
            subject = columns.nth(3).inner_text().strip()
            message = columns.nth(4).inner_text().strip()

            if should_ignore(subject):
                print(f"Ignoring: {subject}")
                continue

            attachments = []
            links = row.locator("a")

            for j in range(links.count()):
                link = links.nth(j)
                href = link.get_attribute("href")
                text = link.inner_text().strip()

                if href and ".pdf" in href.lower():
                    attachments.append({
                        "file_name": text,
                        "url": href
                    })

            msg_data = {
                "student": student,
                "grade": student_config["grade"],
                "section": student_config["section"],
                "date": date,
                "subject": subject,
                "message": message,
                "attachments": attachments
            }

            messages.append(msg_data)

    return messages