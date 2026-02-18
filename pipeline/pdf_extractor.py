from pypdf import PdfReader


def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        full_text = ""

        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
                
        return full_text.strip()

    except Exception as e:
        print(f"PDF extraction failed for {file_path}: {e}")
        return ""