import os
import shutil

import webview

from normalize_docx_styles import fix_docx
from script import docx_to_revista_html

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCX_DIR = os.path.join(BASE_DIR, "docx")
HTML_DIR = os.path.join(BASE_DIR, "html")


class Api:
    def pick_files(self):
        window = webview.windows[0]
        result = window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=True,
            file_types=("Documentos Word (*.docx)", "Todos los archivos (*.*)"),
        )
        return list(result) if result else []

    def convert(self, paths):
        os.makedirs(DOCX_DIR, exist_ok=True)
        os.makedirs(HTML_DIR, exist_ok=True)

        results = []
        for path in paths:
            filename = os.path.basename(path)
            try:
                target_path = os.path.join(DOCX_DIR, filename)
                if os.path.abspath(path) != os.path.abspath(target_path):
                    shutil.copyfile(path, target_path)

                fix_docx(target_path)

                name_without_ext = os.path.splitext(filename)[0]
                output_html = os.path.join(HTML_DIR, f"{name_without_ext}.html")
                html_final = docx_to_revista_html(target_path, output_html)

                results.append({
                    "path": path,
                    "ok": True,
                    "message": "Convertido correctamente",
                    "output_path": output_html,
                    "html": html_final,
                })
            except Exception as e:
                results.append({
                    "path": path,
                    "ok": False,
                    "message": str(e),
                    "output_path": None,
                    "html": None,
                })

        return results

    def save_html(self, html_content, suggested_name):
        window = webview.windows[0]
        result = window.create_file_dialog(
            webview.SAVE_DIALOG,
            directory=HTML_DIR,
            save_filename=suggested_name,
            file_types=("Archivos HTML (*.html)", "Todos los archivos (*.*)"),
        )
        if not result:
            return None

        path = result[0] if isinstance(result, (list, tuple)) else result
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return path


if __name__ == "__main__":
    api = Api()
    webview.create_window(
        "DOCX a HTML - Revista Científica",
        os.path.join(BASE_DIR, "desktop_ui.html"),
        js_api=api,
        width=1100,
        height=750,
        min_size=(800, 500),
    )
    webview.start()
