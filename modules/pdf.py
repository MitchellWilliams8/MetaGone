from pathlib import Path
from pypdf import PdfReader, PdfWriter


def scrub_pdf(src_path: Path, dest_path: Path) -> dict:
    """Strips information and XMP XML streams from PDF file structures.
    """
    reader = PdfReader(src_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    raw_meta = dict(reader.metadata) if reader.metadata else {}
    detected = bool(raw_meta)

    writer.add_metadata({})

    with open(dest_path, "wb") as f:
        writer.write(f)

    scrubbed_keys = [
        f"{k.lstrip('/')}={v}"
        for k, v in raw_meta.items()
        if not k.startswith("/_")
    ]

    return {
        "file": src_path.name,
        "type": "PDF",
        "metadata_detected": detected,
        "tags_scrubbed": scrubbed_keys,
        "status": "Sanitized",
    }