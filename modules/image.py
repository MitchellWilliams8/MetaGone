from pathlib import Path

def scrub_image(src_path: Path, dest_path: Path) -> dict:
    """Sanitizes raster images by purging EXIF/XMP blocks and internal format chunks.
    """
    with Image.open(src_path) as img:
        exif = img.getexif()
        metadata_found = len(exif) > 0 or bool(img.info)

        img.info.clear()

        ext = src_path.suffix.lower()
        if ext in [".jpg", ".jpeg"]:
            img.save(dest_path, format="JPEG", exif=b"", quality=95)
        elif ext == ".png":
            img.save(dest_path, format="PNG")
        elif ext == ".webp":
            img.save(dest_path, format="WEBP", exif=b"")
        else:
            img.save(dest_path)

    return {
        "file": src_path.name,
        "type": "Image",
        "metadata_detected": metadata_found,
        "status": "Sanitized",
    }