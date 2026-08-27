from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.table import Table
import html
import os
import glob

# -------------------------------------------------
# ITERAR BLOQUES (PÁRRAFOS + TABLAS EN ORDEN REAL)
# -------------------------------------------------

def iter_block_items(doc):
    for child in doc.element.body.iterchildren():
        if child.tag == qn('w:p'):
            yield Paragraph(child, doc)
        elif child.tag == qn('w:tbl'):
            yield Table(child, doc)

# -------------------------------------------------
# HIPERVÍNCULOS
# -------------------------------------------------

def get_hyperlink(run):
    r = run._r
    parent = r.getparent()
    if parent.tag == qn('w:hyperlink'):
        rel_id = parent.get(qn('r:id'))
        if rel_id:
            return run.part.rels[rel_id].target_ref
    return None

# -------------------------------------------------
# RUN → HTML
# -------------------------------------------------

def run_to_html(run):
    if not run.text:
        return ""

    text = html.escape(run.text)
    url = get_hyperlink(run)

    if run.font.superscript:
        text = f"<sup>{text}</sup>"
    elif run.font.subscript:
        text = f"<sub>{text}</sub>"

    if run.italic:
        text = f"<em>{text}</em>"

    if run.bold:
        text = f"<strong>{text}</strong>"

    if url:
        text = f'<a href="{url}" target="_blank">{text}</a>'

    return text

def paragraph_to_html(paragraph):
    return "".join(run_to_html(r) for r in paragraph.runs).strip()

# -------------------------------------------------
# TABLAS
# -------------------------------------------------

def row_to_html(row, cell_tag):
    html_row = "<tr>"
    for cell in row.cells:
        cell_content = ""
        for p in cell.paragraphs:
            cell_content += paragraph_to_html(p) + "<br>"
        html_row += f"<{cell_tag}>{cell_content}</{cell_tag}>"
    html_row += "</tr>\n"
    return html_row

def table_to_html(table):
    rows = table.rows
    if not rows:
        return "<table>\n</table>"

    html_table = "<table>\n<thead>\n"
    html_table += row_to_html(rows[0], "th")
    html_table += "</thead>\n<tbody>\n"
    for row in rows[1:]:
        html_table += row_to_html(row, "td")
    html_table += "</tbody>\n</table>"
    return html_table

# -------------------------------------------------
# DETECTAR LISTAS
# -------------------------------------------------

def get_list_type(paragraph):
    """
    Retorna 'ol' para listas numeradas, 'ul' para viñetas, o None si no es lista.
    """
    p = paragraph._p
    pPr = p.pPr
    if pPr is not None and pPr.numPr is not None:
        # Intentamos distinguir por el estilo si es posible
        style = paragraph.style.name.lower()
        if any(x in style for x in ["number", "número", "numeración"]):
            return "ol"
        # Si tiene numPr pero no es claramente número, suele ser viñeta o lista genérica
        return "ul" 
    
    # Algunos documentos usan estilos pero no numPr explícito en el XML
    style = paragraph.style.name.lower()
    if "list bullet" in style or "viñeta" in style: return "ul"
    if "list numbering" in style or "numeración" in style: return "ol"
    
    return None

def flush_list(list_type, items):
    if not items:
        return ""
    tag = list_type if list_type else "ul"
    html_list = f"<{tag}>\n"
    for item in items:
        html_list += f"  <li>{item}</li>\n"
    html_list += f"</{tag}>\n"
    return html_list

# -------------------------------------------------
# CONVERSIÓN PRINCIPAL
# -------------------------------------------------

def docx_to_revista_html(docx_path, output_html):
    doc = Document(docx_path)

    title_es = ""
    title_en = ""

    authors = []
    affiliations = []

    resumen = []
    abstract = []
    body = []

    in_resumen = False
    in_abstract = False
    authors_done = False

    current_list_type = None
    current_list_items = []

    for block in iter_block_items(doc):

        if isinstance(block, Table):
            # Flush list before table
            if current_list_items:
                body.append(flush_list(current_list_type, current_list_items))
                current_list_items = []
                current_list_type = None
            
            body.append(table_to_html(block))
            continue

        style = block.style.name
        text = block.text.strip()
        html_text = paragraph_to_html(block)

        if not text:
            continue

        list_type = get_list_type(block)

        # Si el bloque actual NO es una lista del mismo tipo que la anterior, cerramos la lista previa
        if list_type != current_list_type:
            if current_list_items:
                list_html = flush_list(current_list_type, current_list_items)
                if in_resumen: resumen.append(list_html)
                elif in_abstract: abstract.append(list_html)
                else: body.append(list_html)
                current_list_items = []
            current_list_type = list_type

        # Si es un elemento de lista, lo acumulamos
        if list_type:
            current_list_items.append(html_text)
            continue

        # TÍTULOS
        if style == "Title":
            title_es = html_text
            continue

        if style == "Subtitle":
            title_en = html_text
            authors_done = False
            continue

        # SECCIONES
        if style.startswith("Heading"):
            heading = text.upper()

            if "RESUMEN" in heading:
                in_resumen = True
                in_abstract = False
                authors_done = True
                resumen.append("<h3>RESUMEN</h3>")
                continue

            if "ABSTRACT" in heading:
                in_resumen = False
                in_abstract = True
                abstract.append("<h3>ABSTRACT</h3>")
                continue

            in_resumen = False
            in_abstract = False
            authors_done = True
            body.append(f"<h2>{html_text}</h2>")
            continue

        # AUTORES / AFILIACIONES
        if not authors_done:
            if "@" in text or "orcid" in text.lower():
                affiliations.append(f"<p>{html_text}</p>")
            else:
                authors.append(f"<p>{html_text}</p>")
            continue

        # CONTENIDO (Párrafos normales fuera de listas)
        if in_resumen:
            resumen.append(f"<p>{html_text}</p>")
        elif in_abstract:
            abstract.append(f"<p>{html_text}</p>")
        else:
            body.append(f"<p>{html_text}</p>")

    # Flush any remaining list at the end
    if current_list_items:
        list_html = flush_list(current_list_type, current_list_items)
        if in_resumen: resumen.append(list_html)
        elif in_abstract: abstract.append(list_html)
        else: body.append(list_html)

    # -------------------------------------------------
    # HTML FINAL CON ESTILOS INCRUSTADOS
    # -------------------------------------------------

    html_final = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_es}</title>

<style>
body {{
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f9f9f9;
}}

h1, h2, h3, h4 {{
    color: #09232B;
    font-weight: 700;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}}

h1 {{
    font-size: 2.2em;
    border-bottom: 2px solid #09232B;
    padding-bottom: 10px;
    background-color: #D9D9D9;
}}

h2 {{
    font-size: 1.8em;
    border-left: 4px solid #09232B;
    padding-left: 10px;
    background-color: #D9D9D9;
}}

h3 {{
    font-size: 1.4em;
    background-color: #D9D9D9;
}}

.authors p {{
    font-size: 1.1em;
    font-weight: bold;
    color: #09232B;
}}

.author-affiliation {{
    font-style: italic;
    color: #7f8c8d;
    margin-bottom: 20px;
}}

.resumen, .abstract {{
    background-color: #09232B;
    padding: 15px;
    border-radius: 5px;
    margin: 20px 0;
    color: #FFFFFF;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 30px 0;
    font-size: 0.95em;
    background-color: #ffffff;
    border-left: 6px solid #09232B; 
}}

thead th {{
    background-color: #e6e6e6;
    color: #000000;
    padding: 14px 12px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid #cccccc;
}}

tbody tr {{ 
    border-bottom: 1px solid #e0e0e0;
}}

tbody tr:nth-child(even) {{
    background-color: #f7f7f7;
}}

tbody tr:nth-child(odd) {{ 
    background-color: #ffffff;
}}

td {{
    padding: 14px 12px;
    vertical-align: top;
    line-height: 1.6;
}}

caption {{
    caption-side: top;
    background-color: #e6e6e6;
    padding: 10px 12px;
    font-weight: bold;
    text-align: left;
    color: #000000;
    border-left: 6px solid #09232B;
    margin-bottom: 8px;
}}




a {{
    color: #0066cc;
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

ul, ol {{
    margin-bottom: 20px;
    padding-left: 40px;
}}

li {{
    margin-bottom: 8px;
}}

.resumen ul, .resumen ol, .abstract ul, .abstract ol {{
    color: #FFFFFF;
}}

@media (max-width: 768px) {{
    body {{
        padding: 10px;
    }}

    h1 {{
        font-size: 1.8em;
    }}

    h2 {{
        font-size: 1.5em;
    }}
}}
</style>

</head>
<body>

<h1>{title_es}</h1>
<h2>{title_en}</h2>

<div class="authors">
{''.join(authors)}
</div>

<div class="author-affiliation">
{''.join(affiliations)}
</div>

<div class="resumen">
{''.join(resumen)}
</div>

<div class="abstract">
{''.join(abstract)}
</div>

{''.join(body)}

</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_final)

    print("HTML generado correctamente con estilos.")
    return html_final

# -------------------------------------------------
# EJECUCIÓN
# -------------------------------------------------

DOCX_DIR = "docx"
HTML_DIR = "html"

if __name__ == "__main__":
    os.makedirs(HTML_DIR, exist_ok=True)

    docx_files = glob.glob(os.path.join(DOCX_DIR, "*.docx"))

    if not docx_files:
        print(f"No se encontraron archivos .docx en '{DOCX_DIR}/'.")

    for docx_path in docx_files:
        filename = os.path.basename(docx_path)
        if filename.startswith("~$"):
            continue

        name_without_ext = os.path.splitext(filename)[0]
        output_html = os.path.join(HTML_DIR, f"{name_without_ext}.html")

        print(f"Convirtiendo: {filename}")
        docx_to_revista_html(docx_path, output_html)
