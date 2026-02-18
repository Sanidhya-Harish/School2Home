import hashlib


def generate_circular_hash(file_name, extracted_text, file_size=None):
    """
    Generate strong unique fingerprint for circular.
    Uses combination of:
    - file name
    - extracted text
    - optional file size
    """

    content = f"{file_name}||{extracted_text}"

    if file_size:
        content += f"||{file_size}"

    return hashlib.sha256(content.encode("utf-8")).hexdigest()