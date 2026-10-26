from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


def scrub_docx(src_path: Path, dest_path: Path) -> dict:
    """Sanitizes OpenXML DOCX files by stripping identity, revision, and environment metadata from internal XML properties.
    """
    discovered_tags = {}

    with (
        zipfile.ZipFile(src_path, "r") as zin,
        zipfile.ZipFile(dest_path, "w", compression=zipfile.ZIP_DEFLATED) as zout,
    ):
        for item in zin.infolist():
            content = zin.read(item.filename)

            if item.filename == "docProps/core.xml":
                root = ET.fromstring(content)
                for elem in list(root):
                    tag_name = elem.tag.split("}")[-1]
                    if elem.text and elem.text.strip():
                        discovered_tags[f"core:{tag_name}"] = elem.text
                        elem.text = ""
                content = ET.tostring(
                    root, encoding="utf-8", xml_declaration=True
                )

            elif item.filename == "docProps/app.xml":
                root = ET.fromstring(content)
                for elem in list(root):
                    tag_name = elem.tag.split("}")[-1]
                    if (
                        tag_name in ["Company", "Manager", "Template"]
                        and elem.text
                    ):
                        discovered_tags[f"app:{tag_name}"] = elem.text
                        elem.text = ""
                    elif tag_name == "TotalTime" and elem.text:
                        discovered_tags[f"app:TotalTime"] = elem.text
                        elem.text = "0"
                content = ET.tostring(
                    root, encoding="utf-8", xml_declaration=True
                )

            zout.writestr(item, content)

    return {
        "file": src_path.name,
        "type": "DOCX",
        "metadata_detected": len(discovered_tags) > 0,
        "tags_scrubbed": discovered_tags,
        "status": "Sanitized",
    }