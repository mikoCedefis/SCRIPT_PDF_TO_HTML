import glob
import os
import unicodedata

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Pt, RGBColor

DOCX_DIR = "docx"

SECTION_KEYWORDS = {
    "RESUMEN", "ABSTRACT",
    "INTRODUCCION",
    "METODOS", "METODOLOGIA", "MATERIALES Y METODOS",
    "RESULTADOS",
    "DISCUSION",
    "CONCLUSION", "CONCLUSIONES",
    "REFERENCIAS", "REFERENCIAS BIBLIOGRAFICAS",
    "AGRADECIMIENTOS",
}


def normalize_text(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.upper().strip()


def is_bold(paragraph):
    runs = [r for r in paragraph.runs if r.text.strip()]
    return bool(runs) and all(r.bold for r in runs)


def ensure_style(doc, name, base):
    if name in {s.name for s in doc.styles if s.type == WD_STYLE_TYPE.PARAGRAPH}:
        return doc.styles[name]

    style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    style.base_style = doc.styles["Normal"]
    style.font.bold = base.get("bold")
    style.font.italic = base.get("italic")
    if base.get("size"):
        style.font.size = Pt(base["size"])
    if base.get("font_name"):
        style.font.name = base["font_name"]
    if base.get("color"):
        style.font.color.rgb = RGBColor.from_string(base["color"])
    return style


def fix_docx(path):
    doc = Document(path)

    title_style = ensure_style(doc, "Title", {"bold": True, "size": 36})
    subtitle_style = ensure_style(
        doc, "Subtitle",
        {"italic": True, "size": 24, "font_name": "Georgia", "color": "666666"},
    )
    ensure_style(doc, "Heading 2", {"bold": True, "size": 16})

    paragraphs = [p for p in doc.paragraphs if p.text.strip()]
    changed = False

    if paragraphs and paragraphs[0].style.name != "Title":
        paragraphs[0].style = title_style
        changed = True

    if len(paragraphs) > 1 and paragraphs[1].style.name != "Subtitle":
        paragraphs[1].style = subtitle_style
        changed = True

    for p in paragraphs[2:]:
        if p.style.name.startswith("Heading"):
            continue
        if normalize_text(p.text) in SECTION_KEYWORDS and is_bold(p):
            p.style = doc.styles["Heading 2"]
            changed = True

    if changed:
        doc.save(path)
    return changed


if __name__ == "__main__":
    for path in sorted(glob.glob(os.path.join(DOCX_DIR, "*.docx"))):
        filename = os.path.basename(path)
        if filename.startswith("~$"):
            continue
        changed = fix_docx(path)
        print(f"{'Actualizado' if changed else 'Sin cambios'}: {filename}")
